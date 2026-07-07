from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
# 【追加】日付を扱うためのモジュール
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# データベースの設計図（モデル）
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False) 
    # 【追加】期限を保存するカラム（日付型、期限なしも許容するため nullable=True）
    due_date = db.Column(db.Date, nullable=True)

# アプリ起動時にデータベースを作成
with app.app_context():
    db.create_all()

# 一覧表示機能（トップページ）
@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

# タスク登録機能
@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    # 【追加】フォームから入力された期限（文字列）を取得
    due_date_str = request.form.get('due_date')
    
    if title:
        due_date = None
        # 期限が入力されている場合、文字列から日付オブジェクトに変換
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            
        # 【変更】due_dateを指定して新しいタスクを作成
        new_task = Task(title=title, due_date=due_date)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index'))

# タスクの完了・未完了を切り替える機能
@app.route('/complete/<int:task_id>')
def complete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index'))

# タスクを削除する機能
@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)