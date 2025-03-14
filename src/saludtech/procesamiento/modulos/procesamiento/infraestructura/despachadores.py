import pulsar
from pulsar.schema import *

from saludtech.procesamiento.modulos.procesamiento.infraestructura.schema.v1.eventos import EventoAnonimizacionFallidaPayload, EventoAnonimizacionPayload, EventoAnonimizacionIniciada, EventoAnonimizacion, EventoAnonimizacionFallida, EventoAnonimizacionIniciadaPayload
from saludtech.procesamiento.modulos.procesamiento.infraestructura.schema.v1.comandos import AjusteContrastePayload, ComandoIniciarAnonimizacion, ComandoIniciarAnonimizacionPayload, ConfiguracionAnonimizacionPayload, MetadatosImagenPayload, ReferenciaAlmacenamientoPayload, ResolucionPayload
from saludtech.procesamiento.seedwork.infraestructura import utils
from saludtech.procesamiento.seedwork.infraestructura.despachadores import DespachadorBase, publicar_mensaje
from saludtech.procesamiento.modulos.procesamiento.aplicacion.comandos.iniciar_anonimizacion import IniciarAnonimizacion

import datetime

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

class Despachador(DespachadorBase):
    def _publicar_mensaje(self, mensaje, topico, schema):
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        publicador = cliente.create_producer(topico, schema=schema)
        publicador.send(mensaje)
        cliente.close()

    def publicar_evento(self, evento, topico):
        if isinstance(evento, EventoAnonimizacionIniciada):
            payload = EventoAnonimizacionIniciadaPayload(
                id=str(evento.data.id),
                nombre_paciente = evento.data.nombre_paciente,
                cedula = evento.data.cedula,
                referencia_entrada=evento.data.referencia_entrada,
                configuracion=evento.data.configuracion,
                metadatos=evento.data.metadatos,
                timestamp=int(datetime.datetime.now().timestamp())
            )
            evento_integracion = EventoAnonimizacionIniciada(data=payload)
            self._publicar_mensaje(evento_integracion, topico, AvroSchema(EventoAnonimizacionIniciada))
        elif isinstance(evento, EventoAnonimizacion):
            payload = EventoAnonimizacionPayload(
                id=str(evento.data.id),
                nombre_paciente = evento.data.nombre_paciente,
                cedula = evento.data.cedula,
                referencia_entrada=evento.data.referencia_entrada,
                configuracion=evento.data.configuracion,
                metadatos=evento.data.metadatos,
                timestamp=int(datetime.datetime.now().timestamp())
            )
            evento_integracion = EventoAnonimizacion(data=payload)
            self._publicar_mensaje(evento_integracion, topico, AvroSchema(EventoAnonimizacion))
        elif isinstance(evento, EventoAnonimizacionFallida):
            payload = EventoAnonimizacionFallidaPayload(
                id=str(evento.id),
                motivo_fallo=evento.motivo_fallo,
                timestamp=int(unix_time_millis(evento.timestamp))
            )
            evento_integracion = EventoAnonimizacionFallida(data=payload)
            self._publicar_mensaje(evento_integracion, topico, AvroSchema(EventoAnonimizacionFallida))

    
    def publicar_comando(self, comando, topico):
        publicar_mensaje(comando, topico)

@publicar_mensaje.register
def _(comando: IniciarAnonimizacion, topico):
    
    payload = ComandoIniciarAnonimizacionPayload(
        id=str(comando.id),
        id_solicitud=str(comando.id_solicitud),
        usuario=str(comando.usuario),
        nombre= comando.nombre,
        cedula= int(comando.cedula),
        metadatos=MetadatosImagenPayload(
            id=str(comando.id),
            modalidad=comando.metadatos.modalidad,
            region=comando.metadatos.region,
            resolucion=ResolucionPayload(
                ancho = comando.metadatos.resolucion.ancho,
                alto = comando.metadatos.resolucion.alto,
                dpi = comando.metadatos.resolucion.dpi
            ),
            fecha_adquisicion=comando.metadatos.fecha_adquisicion
        ),
        configuracion=ConfiguracionAnonimizacionPayload(
            id=str(comando.id),
            nivel_anonimizacion = comando.configuracion.nivel_anonimizacion,
            formato_salida = comando.configuracion.formato_salida,
            ajustes_contraste = AjusteContrastePayload(
                brillo = comando.configuracion.ajustes_contraste.brillo,
                contraste = comando.configuracion.ajustes_contraste.contraste
            ),
            algoritmo = comando.configuracion.algoritmo_usado,
        ),
        referencia_entrada=ReferenciaAlmacenamientoPayload(
            id=str(comando.id),
            nombre_bucket = comando.referencia_entrada.nombre_bucket,
            llave_objeto = comando.referencia_entrada.llave_objeto,
            proveedor_almacenamiento = comando.referencia_entrada.proveedor_almacenamiento
        )
    )
    comando_integracion = ComandoIniciarAnonimizacion(data=payload)
    despachador = Despachador()
    despachador._publicar_mensaje(comando_integracion, topico, AvroSchema(ComandoIniciarAnonimizacion))
