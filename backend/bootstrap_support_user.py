from getpass import getpass

from backend.database import SessionLocal
from backend import models
from backend.utils import hash_password, validate_password_strength


def main():
    db = SessionLocal()
    try:
        existing_support = db.query(models.Usuario).filter(models.Usuario.rol == 'soporte').first()
        if existing_support:
            print(f"Ya existe un usuario de soporte: {existing_support.username}")
            return

        username = input('Usuario de soporte inicial: ').strip()
        if not username:
            print('El usuario es obligatorio')
            return

        password = getpass('Contraseña inicial de soporte: ')
        confirm = getpass('Confirma la contraseña: ')
        if password != confirm:
            print('Las contraseñas no coinciden')
            return

        try:
            validate_password_strength(password)
        except ValueError as exc:
            print(str(exc))
            return

        user = models.Usuario(
            username=username,
            password=hash_password(password),
            rol='soporte',
            status='activo',
            must_change_password=False,
            created_by='bootstrap',
        )
        db.add(user)
        db.commit()
        print(f"Usuario de soporte creado: {username}")
    finally:
        db.close()


if __name__ == '__main__':
    main()
