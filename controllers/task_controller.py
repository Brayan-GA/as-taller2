"""
Controlador de Tareas - Maneja la lógica de negocio de las tareas

Este archivo contiene todas las rutas y lógica relacionada con las tareas.
Representa la capa "Controlador" en la arquitectura MVC.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models import task
from models.task import Task
from app import db


def register_routes(app):
    """
    Registra todas las rutas del controlador de tareas en la aplicación Flask
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    
    @app.route('/')
    def index():
        """
        Ruta principal - Redirige a la lista de tareas
        
        Returns:
            Response: Redirección a la lista de tareas
        """
        return redirect(url_for('task_list'))
    
    
    @app.route('/tasks')
    def task_list():
        """
        Muestra la lista de todas las tareas

        Query Parameters:
            filter (str): Filtro para mostrar tareas ('all', 'pending', 'completed')
            sort (str): Ordenamiento ('date', 'title', 'created')

        Returns:
            str: HTML renderizado con la lista de tareas
        """
        # TODO: Implementar en Versión 1
        # Obtener parámetros de filtro y ordenamiento
        filter_type = request.args.get('filter', 'all')
        sort_by = request.args.get('sort', 'created')
        
        query = Task.query

        # Filtro por estado
        if filter_type == 'pending':
            query = query.filter_by(completed=False)
        elif filter_type == 'completed':
            query = query.filter_by(completed=True)

        # Ordenamiento
        if sort_by == 'title':
            query = query.order_by(Task.title)
        elif sort_by == 'date':
            query = query.order_by(Task.due_date)
        else:  # created
            query = query.order_by(Task.id)

        tasks = query.all()

        # Datos para pasar a la plantilla
        context = {
            'tasks': tasks,
            'filter_type': filter_type,
            'sort_by': sort_by,
            'total_tasks': len(tasks),
            'pending_count': Task.query.filter_by(completed=False).count(),
            'completed_count': Task.query.filter_by(completed=True).count()
        }

        return render_template('task_list.html', **context)
 
    
    @app.route('/tasks/new', methods=['GET', 'POST'])
    def task_create():
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            due_date_str = request.form.get('due_date')

            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else None
            except ValueError:
                flash('Formato de fecha inválido', 'error')
                return redirect(url_for('task_create'))

            new_task = Task(title=title, description=description, due_date=due_date)
            db.session.add(new_task)
            db.session.commit()
            flash('Tarea creada exitosamente', 'success')
            return redirect(url_for('task_list'))

        # GET: mostrar formulario vacío
        return render_template('task_form.html', task=None)
    
    
    @app.route('/tasks/<int:task_id>')
    def task_detail(task_id):

        task = Task.query.get_or_404(task_id)
        return render_template('task_detail.html', task=task)
    
    
    @app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
    def task_edit(task_id):
        """
        Edita una tarea existente

        """
        task = Task.query.get_or_404(task_id)

        if request.method == 'POST':
            task.title = request.form.get('title')
            task.description = request.form.get('description')
            due_date_str = request.form.get('due_date')
            # completed field will be updated below based on checkbox
            task.completed = bool(request.form.get('completed'))

            # Validar fecha
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else None
            except ValueError:
                flash('Formato de fecha inválido', 'error')
                return redirect(url_for('task_edit', task_id=task.id))

            db.session.commit()
            flash('Tarea actualizada exitosamente', 'success')
            return redirect(url_for('task_list'))

        # GET: mostrar formulario con datos actuales
        return render_template('task_form.html', task=task)
    
    
    @app.route('/tasks/<int:task_id>/delete', methods=['POST'])
    def task_delete(task_id):
        """
        Elimina una tarea

        """
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        flash('Tarea eliminada', 'success')
        return redirect(url_for('task_list'))
    
    
    @app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
    def task_toggle(task_id):
        """
        Cambia el estado de completado de una tarea

        """
        task = Task.query.get_or_404(task_id)
        task.completed = not task.completed
        db.session.commit()
        return redirect(url_for('task_list'))
    
    
    # Rutas adicionales para versiones futuras
    
    @app.route('/api/tasks', methods=['GET'])
    def api_tasks():

        # TODO: para versiones futuras
        return jsonify({
            'tasks': [],
            'message': 'API en desarrollo - Implementar en versiones futuras'
        })
    
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Maneja errores 404 - Página no encontrada"""
        return render_template('404.html'), 404
    
    
    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores 500 - Error interno del servidor"""
        db.session.rollback()
        return render_template('500.html'), 500

