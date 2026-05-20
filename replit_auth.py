import jwt
import os
import uuid
from functools import wraps
from urllib.parse import urlencode

from flask import g, session, redirect, request, render_template, url_for, jsonify
from flask_dance.consumer import (
    OAuth2ConsumerBlueprint,
    oauth_authorized,
    oauth_error,
)
from flask_dance.consumer.storage import BaseStorage
from flask_login import LoginManager, login_user, logout_user, current_user
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from sqlalchemy.exc import NoResultFound
from werkzeug.local import LocalProxy

from app import app, db
from models import OAuth, User

login_manager = LoginManager(app)

issuer_url = os.environ.get('ISSUER_URL', "https://replit.com/oidc")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class UserSessionStorage(BaseStorage):
    def get(self, blueprint):
        try:
            token = db.session.query(OAuth).filter_by(
                user_id=current_user.get_id(),
                browser_session_key=g.browser_session_key,
                provider=blueprint.name,
            ).one().token
        except NoResultFound:
            token = None
        return token

    def set(self, blueprint, token):
        db.session.query(OAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name,
        ).delete()
        new_model = OAuth()
        new_model.user_id = current_user.get_id()
        new_model.browser_session_key = g.browser_session_key
        new_model.provider = blueprint.name
        new_model.token = token
        db.session.add(new_model)
        db.session.commit()

    def delete(self, blueprint):
        db.session.query(OAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name).delete()
        db.session.commit()

def make_replit_blueprint():
    # If running locally without Replit OIDC, provide a simple dev blueprint
    try:
        repl_id = os.environ['REPL_ID']
    except KeyError:
        from flask import Blueprint
        from types import SimpleNamespace
        dev_bp = Blueprint('replit_auth', __name__)

        @dev_bp.before_app_request
        def set_dev_session():
            if '_browser_session_key' not in session:
                session['_browser_session_key'] = uuid.uuid4().hex
            session.modified = True
            g.browser_session_key = session['_browser_session_key']
            # provide a lightweight token object so require_login works
            g.flask_dance_replit = SimpleNamespace(token={'expires_in': 999999})

        @dev_bp.route('/login')
        def login():
            # Simple developer login: create or fetch a user with id 'dev-user'
            user_claims = {
                'sub': os.environ.get('DEV_USER_ID', 'dev-user'),
                'email': os.environ.get('DEV_USER_EMAIL', 'dev@example.com'),
                'first_name': os.environ.get('DEV_USER_FIRST', 'Dev'),
                'last_name': os.environ.get('DEV_USER_LAST', 'User'),
            }
            user = save_user(user_claims)
            login_user(user)
            return redirect(url_for('index'))

        @dev_bp.route('/logout')
        def logout():
            logout_user()
            session.clear()
            return redirect(url_for('index'))

        return dev_bp

    # Production/Replit OIDC blueprint
    replit_bp = OAuth2ConsumerBlueprint(
        "replit_auth",
        __name__,
        client_id=repl_id,
        client_secret=None,
        base_url=issuer_url,
        authorization_url_params={
            "prompt": "login consent",
        },
        token_url=issuer_url + "/token",
        token_url_params={
            "auth": (),
            "include_client_id": True,
        },
        auto_refresh_url=issuer_url + "/token",
        auto_refresh_kwargs={
            "client_id": repl_id,
        },
        authorization_url=issuer_url + "/auth",
        use_pkce=True,
        code_challenge_method="S256",
        scope=["openid", "profile", "email", "offline_access"],
        storage=UserSessionStorage(),
    )

    @replit_bp.before_app_request
    def set_applocal_session():
        if '_browser_session_key' not in session:
            session['_browser_session_key'] = uuid.uuid4().hex
        session.modified = True
        g.browser_session_key = session['_browser_session_key']
        g.flask_dance_replit = replit_bp.session

    @replit_bp.route("/logout")
    def logout():
        try:
            del replit_bp.token
        except (KeyError, AttributeError):
            pass
        
        logout_user()
        session.clear()

        end_session_endpoint = issuer_url + "/session/end"
        encoded_params = urlencode({
            "client_id": repl_id,
            "post_logout_redirect_uri": request.url_root,
        })
        logout_url = f"{end_session_endpoint}?{encoded_params}"

        return redirect(logout_url)

    @replit_bp.route("/error")
    def error():
        return render_template("error.html"), 403

    return replit_bp

def save_user(user_claims):
    user = User()
    user.id = user_claims['sub']
    user.email = user_claims.get('email')
    user.first_name = user_claims.get('first_name')
    user.last_name = user_claims.get('last_name')
    user.profile_image_url = user_claims.get('profile_image_url')
    merged_user = db.session.merge(user)
    db.session.commit()
    return merged_user

@oauth_authorized.connect
def logged_in(blueprint, token):
    user_claims = jwt.decode(token['id_token'], options={"verify_signature": False})
    user = save_user(user_claims)
    login_user(user)
    blueprint.token = token
    next_url = session.pop("next_url", None)
    if next_url is not None:
        return redirect(next_url)

@oauth_error.connect
def handle_error(blueprint, error, error_description=None, error_uri=None):
    return redirect(url_for('replit_auth.error'))

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_api_request = request.path.startswith('/api/')
        
        if not current_user.is_authenticated:
            if is_api_request:
                return jsonify({"error": "Unauthorized"}), 401
            session["next_url"] = get_next_navigation_url(request)
            return redirect(url_for('replit_auth.login'))

        if replit.token is None:
            if is_api_request:
                return jsonify({"error": "Unauthorized"}), 401
            session["next_url"] = get_next_navigation_url(request)
            return redirect(url_for('replit_auth.login'))

        expires_in = replit.token.get('expires_in', 0)
        if expires_in < 0:
            refresh_token_url = issuer_url + "/token"
            try:
                token = replit.refresh_token(token_url=refresh_token_url, client_id=os.environ['REPL_ID'])
            except InvalidGrantError:
                if is_api_request:
                    return jsonify({"error": "Unauthorized"}), 401
                session["next_url"] = get_next_navigation_url(request)
                return redirect(url_for('replit_auth.login'))
            replit.token_updater(token)

        return f(*args, **kwargs)

    return decorated_function

def get_next_navigation_url(request):
    is_navigation_url = request.headers.get('Sec-Fetch-Mode') == 'navigate' and request.headers.get('Sec-Fetch-Dest') == 'document'
    if is_navigation_url:
        return request.url
    return request.referrer or request.url

replit = LocalProxy(lambda: g.flask_dance_replit)
