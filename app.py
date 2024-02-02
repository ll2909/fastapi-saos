from fastapi import Depends, FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse
import ssl
import uvicorn

from routes.route import router
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('./certs/cert.pem', keyfile='./certs/key.pem')
app.add_middleware(HTTPSRedirectMiddleware)
app.include_router(router)


if __name__ == "__main__":
    
    uvicorn.run("app:app", host="0.0.0.0", port=443, reload=True, ssl_keyfile="./certs/key.pem", ssl_certfile="./certs/cert.pem") 