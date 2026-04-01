"""Academic domain models.

Models: Estudiante, Docente, Departamento, ProgramaAcademico, Curso,
        SeccionCurso, Matricula, Calificacion, Asistencia,
        CalendarioAcademico, HorarioCurso, HistorialAcademico  (12 models)
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Model 10 – Departamento
# ---------------------------------------------------------------------------
class Departamento(Base):
    __tablename__ = "departamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    codigo: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)

    programas: Mapped[list["ProgramaAcademico"]] = relationship(back_populates="departamento")
    docentes: Mapped[list["Docente"]] = relationship(back_populates="departamento")


# ---------------------------------------------------------------------------
# Model 11 – ProgramaAcademico
# ---------------------------------------------------------------------------
class ProgramaAcademico(Base):
    __tablename__ = "programas_academicos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    codigo: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    nivel: Mapped[str] = mapped_column(String(32), default="pregrado")
    duracion_semestres: Mapped[int] = mapped_column(Integer, default=10)
    departamento_id: Mapped[int | None] = mapped_column(ForeignKey("departamentos.id"))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    departamento: Mapped["Departamento | None"] = relationship(back_populates="programas")
    cursos: Mapped[list["Curso"]] = relationship(back_populates="programa")
    matriculas: Mapped[list["Matricula"]] = relationship(back_populates="programa")


# ---------------------------------------------------------------------------
# Model 12 – Estudiante
# ---------------------------------------------------------------------------
class Estudiante(Base):
    __tablename__ = "estudiantes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    usuario_id: Mapped[str | None] = mapped_column(String(36), index=True)
    nombres: Mapped[str] = mapped_column(String(120), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    matriculas: Mapped[list["Matricula"]] = relationship(back_populates="estudiante")
    historial: Mapped[list["HistorialAcademico"]] = relationship(back_populates="estudiante")
    asistencias: Mapped[list["Asistencia"]] = relationship(back_populates="estudiante")


# ---------------------------------------------------------------------------
# Model 13 – Docente
# ---------------------------------------------------------------------------
class Docente(Base):
    __tablename__ = "docentes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    usuario_id: Mapped[str | None] = mapped_column(String(36))
    nombres: Mapped[str] = mapped_column(String(120), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    especialidad: Mapped[str | None] = mapped_column(String(128))
    departamento_id: Mapped[int | None] = mapped_column(ForeignKey("departamentos.id"))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    departamento: Mapped["Departamento | None"] = relationship(back_populates="docentes")
    secciones: Mapped[list["SeccionCurso"]] = relationship(back_populates="docente")


# ---------------------------------------------------------------------------
# Model 14 – Curso
# ---------------------------------------------------------------------------
class Curso(Base):
    __tablename__ = "cursos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    codigo: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    creditos: Mapped[int] = mapped_column(Integer, default=3)
    descripcion: Mapped[str | None] = mapped_column(Text)
    programa_id: Mapped[str | None] = mapped_column(ForeignKey("programas_academicos.id"))

    programa: Mapped["ProgramaAcademico | None"] = relationship(back_populates="cursos")
    secciones: Mapped[list["SeccionCurso"]] = relationship(back_populates="curso")


# ---------------------------------------------------------------------------
# Model 15 – SeccionCurso
# ---------------------------------------------------------------------------
class SeccionCurso(Base):
    __tablename__ = "secciones_curso"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    curso_id: Mapped[str] = mapped_column(ForeignKey("cursos.id"), nullable=False)
    docente_id: Mapped[str | None] = mapped_column(ForeignKey("docentes.id"))
    semestre: Mapped[str] = mapped_column(String(16), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    cupo_maximo: Mapped[int] = mapped_column(Integer, default=30)
    aula: Mapped[str | None] = mapped_column(String(32))

    curso: Mapped["Curso"] = relationship(back_populates="secciones")
    docente: Mapped["Docente | None"] = relationship(back_populates="secciones")
    matriculas: Mapped[list["Matricula"]] = relationship(back_populates="seccion")
    calificaciones: Mapped[list["Calificacion"]] = relationship(back_populates="seccion")
    horarios: Mapped[list["HorarioCurso"]] = relationship(back_populates="seccion")
    asistencias: Mapped[list["Asistencia"]] = relationship(back_populates="seccion")


# ---------------------------------------------------------------------------
# Model 16 – Matricula
# ---------------------------------------------------------------------------
class Matricula(Base):
    __tablename__ = "matriculas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    estudiante_id: Mapped[str] = mapped_column(ForeignKey("estudiantes.id"), nullable=False)
    programa_id: Mapped[str | None] = mapped_column(ForeignKey("programas_academicos.id"))
    seccion_id: Mapped[str | None] = mapped_column(ForeignKey("secciones_curso.id"))
    estado: Mapped[str] = mapped_column(String(32), default="enrolled")
    fecha_matricula: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    estudiante: Mapped["Estudiante"] = relationship(back_populates="matriculas")
    programa: Mapped["ProgramaAcademico | None"] = relationship(back_populates="matriculas")
    seccion: Mapped["SeccionCurso | None"] = relationship(back_populates="matriculas")


# ---------------------------------------------------------------------------
# Model 17 – Calificacion
# ---------------------------------------------------------------------------
class Calificacion(Base):
    __tablename__ = "calificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    estudiante_id: Mapped[str] = mapped_column(ForeignKey("estudiantes.id"), nullable=False)
    seccion_id: Mapped[str] = mapped_column(ForeignKey("secciones_curso.id"), nullable=False)
    tipo_evaluacion: Mapped[str] = mapped_column(String(64), default="parcial")
    nota: Mapped[float] = mapped_column(Float, nullable=False)
    nota_maxima: Mapped[float] = mapped_column(Float, default=20.0)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    seccion: Mapped["SeccionCurso"] = relationship(back_populates="calificaciones")


# ---------------------------------------------------------------------------
# Model 18 – Asistencia
# ---------------------------------------------------------------------------
class Asistencia(Base):
    __tablename__ = "asistencias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    estudiante_id: Mapped[str] = mapped_column(ForeignKey("estudiantes.id"), nullable=False)
    seccion_id: Mapped[str] = mapped_column(ForeignKey("secciones_curso.id"), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    presente: Mapped[bool] = mapped_column(Boolean, default=True)
    justificado: Mapped[bool] = mapped_column(Boolean, default=False)

    estudiante: Mapped["Estudiante"] = relationship(back_populates="asistencias")
    seccion: Mapped["SeccionCurso"] = relationship(back_populates="asistencias")


# ---------------------------------------------------------------------------
# Model 19 – CalendarioAcademico
# ---------------------------------------------------------------------------
class CalendarioAcademico(Base):
    __tablename__ = "calendarios_academicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    semestre: Mapped[str] = mapped_column(String(16), nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


# ---------------------------------------------------------------------------
# Model 20 – HorarioCurso
# ---------------------------------------------------------------------------
class HorarioCurso(Base):
    __tablename__ = "horarios_curso"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seccion_id: Mapped[str] = mapped_column(ForeignKey("secciones_curso.id"), nullable=False)
    dia_semana: Mapped[str] = mapped_column(String(16), nullable=False)
    hora_inicio: Mapped[str] = mapped_column(String(8), nullable=False)
    hora_fin: Mapped[str] = mapped_column(String(8), nullable=False)
    aula: Mapped[str | None] = mapped_column(String(32))

    seccion: Mapped["SeccionCurso"] = relationship(back_populates="horarios")


# ---------------------------------------------------------------------------
# Model 21 – HistorialAcademico
# ---------------------------------------------------------------------------
class HistorialAcademico(Base):
    __tablename__ = "historial_academico"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    estudiante_id: Mapped[str] = mapped_column(ForeignKey("estudiantes.id"), nullable=False)
    promedio_ponderado: Mapped[float | None] = mapped_column(Float)
    creditos_aprobados: Mapped[int] = mapped_column(Integer, default=0)
    creditos_intentados: Mapped[int] = mapped_column(Integer, default=0)
    estado_academico: Mapped[str] = mapped_column(String(32), default="regular")
    actualizado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    estudiante: Mapped["Estudiante"] = relationship(back_populates="historial")
