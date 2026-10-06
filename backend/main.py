import os
from datetime import datetime,timedelta,timezone
import bcrypt,jwt
from dotenv import load_dotenv
from fastapi import FastAPI,HTTPException,Request,Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,EmailStr
from pymongo import MongoClient
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
load_dotenv()
app=FastAPI(title='Movie Platform API')
FRONTEND_URL=os.getenv('FRONTEND_URL','http://localhost:5173').rstrip('/')
SECRET=os.getenv('JWT_SECRET','dev-secret'); dbname=os.getenv('DATABASE_NAME','movie_platform'); uri=os.getenv('MONGODB_URI','')
db=MongoClient(uri)[dbname] if uri else None
users=db.users if db is not None else None
app.add_middleware(CORSMiddleware,allow_origins=[FRONTEND_URL],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
oauth=OAuth()
if os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_SECRET'):
 oauth.register(name='google',client_id=os.getenv('GOOGLE_CLIENT_ID'),client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',client_kwargs={'scope':'openid email profile'})
class Register(BaseModel): full_name:str; email:EmailStr; password:str
class Login(BaseModel): email:EmailStr; password:str
def tok(u): return jwt.encode({'sub':str(u['_id']),'email':u['email'],'role':u.get('role','user'),'exp':datetime.now(timezone.utc)+timedelta(days=7)},SECRET,algorithm='HS256')
def safe(u): return {'id':str(u['_id']),'full_name':u.get('full_name',''),'email':u['email'],'avatar_url':u.get('avatar_url',''),'role':u.get('role','user')}
def cookie(r,t): r.set_cookie('access_token',t,httponly=True,secure=True,samesite='lax',max_age=604800)
@app.get('/api/health')
def health(): return {'status':'ok'}
@app.post('/api/auth/register')
def register(x:Register,response:Response):
 if users is None: raise HTTPException(503,'Database is not configured')
 email=x.email.lower().strip()
 if len(x.password)<6: raise HTTPException(400,'Password must be at least 6 characters')
 if users.find_one({'email':email}): raise HTTPException(409,'An account with this email already exists')
 u={'full_name':x.full_name.strip(),'email':email,'password_hash':bcrypt.hashpw(x.password.encode(),bcrypt.gensalt()).decode(),'avatar_url':'','role':'user','provider':'password','created_at':datetime.now(timezone.utc)}
 u['_id']=users.insert_one(u).inserted_id; cookie(response,tok(u)); return {'user':safe(u)}
@app.post('/api/auth/login')
def login(x:Login,response:Response):
 if users is None: raise HTTPException(503,'Database is not configured')
 u=users.find_one({'email':x.email.lower().strip()})
 if not u or not u.get('password_hash') or not bcrypt.checkpw(x.password.encode(),u['password_hash'].encode()): raise HTTPException(401,'Invalid email or password')
 cookie(response,tok(u)); return {'user':safe(u)}
@app.post('/api/auth/logout')
def logout(response:Response): response.delete_cookie('access_token'); return {'ok':True}
@app.get('/api/auth/me')
def me(request:Request):
 if users is None: raise HTTPException(503,'Database is not configured')
 t=request.cookies.get('access_token')
 if not t: raise HTTPException(401,'Not logged in')
 try:
  p=jwt.decode(t,SECRET,algorithms=['HS256']); from bson import ObjectId; u=users.find_one({'_id':ObjectId(p['sub'])})
 except Exception: raise HTTPException(401,'Invalid or expired session')
 if not u: raise HTTPException(401,'User not found')
 return {'user':safe(u)}
@app.get('/api/auth/google')
async def google(request:Request):
 if 'google' not in oauth: raise HTTPException(503,'Google Sign-In is not configured yet')
 return await oauth.google.authorize_redirect(request,os.getenv('GOOGLE_REDIRECT_URI'))
@app.get('/api/auth/google/callback')
async def google_cb(request:Request):
 if 'google' not in oauth or users is None: raise HTTPException(503,'Google Sign-In is not configured')
 t=await oauth.google.authorize_access_token(request); info=t.get('userinfo') or await oauth.google.parse_id_token(request,t); email=(info.get('email') or '').lower()
 if not email: raise HTTPException(400,'Google account email unavailable')
 u=users.find_one({'email':email})
 if not u:
  u={'full_name':info.get('name',''),'email':email,'password_hash':'','avatar_url':info.get('picture',''),'role':'user','provider':'google','created_at':datetime.now(timezone.utc)}; u['_id']=users.insert_one(u).inserted_id
 else: users.update_one({'_id':u['_id']},{'$set':{'full_name':info.get('name',u.get('full_name','')),'avatar_url':info.get('picture',u.get('avatar_url',''))}}); u=users.find_one({'_id':u['_id']})
 r=RedirectResponse(FRONTEND_URL); cookie(r,tok(u)); return r
