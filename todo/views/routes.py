from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    """Return the list of todo items"""
    completed_filter = request.args.get('completed')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Todo.query

    if completed_filter is not None:
        completed_filter = completed_filter.lower() == 'true'
        query = query.filter_by(completed=completed_filter)
        #todos = Todo.query.filter_by(completed=completed_filter).all()
    #else:
    #    todos = Todo.query.all()
    #if start_date:
        #query = query.filter(Todo.deadline_at >= datetime.fromisoformat(start_date))
        ##query = query.filter(cast(Todo.deadline_at, DateTime) >= start_date)
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date)
            query = query.filter(Todo.deadline_at >= start_date)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DDTHH:MM:SS"}), 400
    #if end_date:
        #query = query.filter(Todo.deadline_at <= datetime.fromisoformat(end_date))
        ##query = query.filter(cast(Todo.deadline_at, DateTime) <= end_date)
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date)
            query = query.filter(Todo.deadline_at <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DDTHH:MM:SS"}), 400
    
    todos = query.all()

    print(f"Filters - completed: {completed_filter}, start_date: {start_date}, end_date: {end_date}")
    print(f"Todos Retrieved: {[todo.to_dict() for todo in todos]}")

    return jsonify([todo.to_dict() for todo in todos])
    
    #return jsonify([todo.to_dict() for todo in todos])
    """
    todos = Todo.query.all()
    result = []
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)
    """

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Return the details of a todo item"""
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo item and return the created item"""
    allowed_fields = {"title", "description", "completed", "deadline_at"}
    extra_fields = set(request.json.keys()) - allowed_fields

    if extra_fields:
        return jsonify({"error": "Unexpected fields in request"}), 400

    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))

    # Adds a new record to the database or will update an existing record
    db.session.add(todo)
    # Commits the changes to the database
    # This must be called for the changes to be saved
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo item and return the updated item"""
    #if "id" in request.json:
    #    return jsonify({"error": "Cannot modify 'id' field"}), 400

    allowed_fields = {"title", "description", "completed", "deadline_at"}
    extra_fields = set(request.json.keys()) - allowed_fields

    if extra_fields:
        return jsonify({"error": "Unexpected fields in request"}), 400

    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404

    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('descirption', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()

    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo item and return the deleted item"""
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200

    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
 
