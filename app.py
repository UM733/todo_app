from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
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
    due_date = db.Column(db.Date, nullable=True)

# アプリ起動時にデータベースを作成
with app.app_context():
    db.create_all()

# 【修正】一覧表示機能（フィルター対応）
@app.route('/')
def index():
    # URLから filter パラメータを取得（指定がなければ 'all' にする）
    current_filter = request.args.get('filter', 'all')
    
    # フィルター条件に応じてデータベースから取得するデータを切り替える
    if current_filter == 'active':
        # 未完了（completed が False）のタスクだけを取得
        tasks = Task.query.filter_by(completed=False).all()
    elif current_filter == 'completed':
        # 完了済み（completed が True）のタスクだけを取得
        tasks = Task.query.filter_by(completed=True).all()
    else:
        # すべてのタスクを取得
        tasks = Task.query.all()
        current_filter = 'all'

    # HTML側に、タスク一覧と「現在選ばれているフィルター」を渡す
    return render_template('index.html', tasks=tasks, current_filter=current_filter)

# タスク登録機能
@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    due_date_str = request.form.get('due_date')
    
    if title:
        due_date = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            
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
    # 【ヒント】現在のフィルター状態を維持して戻ることも可能ですが、まずはシンプルにトップへ戻します
    return redirect(url_for('index'))

# タスクを削除する機能
@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

# 完了済みのタスクを一括削除する機能
@app.route('/delete_completed')
def delete_completed():
    Task.query.filter_by(completed=True).delete()
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)