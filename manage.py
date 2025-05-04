from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import click

app = create_app()

@click.group()
def cli():
    """Management script for BFL Studios application"""
    pass

@cli.command()
@click.option('--email', prompt=True, help='Admin email address')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@click.option('--first-name', prompt=True, help='Admin first name')
@click.option('--last-name', prompt=True, help='Admin last name')
def create_admin(email, password, first_name, last_name):
    """Create a new admin user"""
    with app.app_context():
        if User.query.filter_by(email=email).first():
            click.echo('Error: Email already registered')
            return

        admin = User(
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            role='admin',
            is_verified=True,
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Admin user {email} created successfully!')

if __name__ == '__main__':
    cli()