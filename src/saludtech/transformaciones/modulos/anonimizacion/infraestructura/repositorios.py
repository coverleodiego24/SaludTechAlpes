""" Repositorios para el manejo de persistencia de objetos de dominio en la capa de infrastructura del dominio de anonimizacion

En este archivo usted encontrará los diferentes repositorios para
persistir objetos dominio (agregaciones) en la capa de infraestructura del dominio de anonimizacion

"""

from saludtech.transformaciones.config.db import db
from saludtech.transformaciones.modulos.anonimizacion.dominio.repositorios import RepositorioImagenesAnonimizadas, RepositorioProcesosAnonimizacion
from saludtech.transformaciones.modulos.anonimizacion.dominio.entidades import ImagenAnonimizada
from saludtech.transformaciones.modulos.anonimizacion.infraestructura.dto import ImagenAnonimizadaDTO
from saludtech.transformaciones.modulos.anonimizacion.infraestructura.mapeadores import MapeadorImagenAnonimizada
from sqlalchemy.exc import NoResultFound
from uuid import UUID

class RepositorioImagenesAnonimizadasSQLite(RepositorioImagenesAnonimizadas):

    def obtener_por_id(self, id: UUID) -> ImagenAnonimizada:
        try:
            imagen_dto = db.session.query(ImagenAnonimizadaDTO).filter_by(id=str(id)).one()
            return MapeadorImagenAnonimizada().dto_a_entidad(imagen_dto)
        except NoResultFound:
            return None

    def obtener_todos(self) -> list[ImagenAnonimizada]:
        imagenes_dto = db.session.query(ImagenAnonimizadaDTO).all()
        mapeador = MapeadorImagenAnonimizada()
        return [mapeador.dto_a_entidad(imagen_dto) for imagen_dto in imagenes_dto]

    def agregar(self, imagen: ImagenAnonimizada):
        try:
            imagen_dto = MapeadorImagenAnonimizada().entidad_a_dto(imagen)
            db.session.add(imagen_dto)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def actualizar(self, imagen: ImagenAnonimizada):
        try:
            imagen_dto = db.session.query(ImagenAnonimizadaDTO).filter_by(id=str(imagen.id)).one_or_none()
            if imagen_dto:
                for key, value in MapeadorImagenAnonimizada().entidad_a_dto(imagen).__dict__.items():
                    #if key != '_sa_instance_state':
                    setattr(imagen_dto, key, value)
            else:
                db.session.add(MapeadorImagenAnonimizada().entidad_a_dto(imagen))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def eliminar(self, id: UUID):
        try:
            imagen_dto = db.session.query(ImagenAnonimizadaDTO).filter_by(id=str(id)).one()
            db.session.delete(imagen_dto)
            db.session.commit()
        except NoResultFound:
            return False
        except Exception as e:
            db.session.rollback()
            raise e

class RepositorioProcesosAnonimizacionSQLite(RepositorioProcesosAnonimizacion):
    # Implementación similar a RepositorioImagenesAnonimizadasSQLite
    ...