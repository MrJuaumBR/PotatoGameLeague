from SETTINGS import *

dataManager()

@app.route("/")
def home():
    current_user = None
    if 'token' in session:
        current_user = User()
        current_user.loadAccessToken(session.get('token'))
    return render_template('home.html',current_user=current_user)

@app.route('/oauth/callback')
def callback():
    current_user = User(request.args['code'])
    session['token'] = current_user.access_token
    return redirect('/')

@app.route('/logout')
def logout():
    if 'token' in session:
        session.clear()
        return redirect('/')
    
@app.route('/u/<userId>')
def user(userId):
    current_user = None
    if 'token' in session:
        current_user = User()
        current_user.loadAccessToken(session.get('token'))
    return render_template("user.html",current_user=current_user)
    

if __name__ == "__main__":
    app.run(debug=True)