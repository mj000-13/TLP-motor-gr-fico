# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from Runtime.types import BrikNativeFunction
import time
import random
import os
import sys

try:
    # Para Windows
    import msvcrt
except ImportError:
    # Para Mac/Linux
    import tty
    import termios
    import select


def native_len(value):
    """Devuelve el tamano de un array (lista) o string."""
    if not hasattr(value, '__len__'):
        raise Exception(u"No se puede aplicar 'len()' a este tipo.")
    return float(len(value))

def native_sleep(ms):
    """Pausa la ejecucion por milisegundos."""
    # time.sleep usa segundos, asi que convertimos
    time.sleep(ms / 1000.0)
    return None # Las funciones nativas pueden no devolver nada

def native_rand(min_val, max_val):
    """Devuelve un entero aleatorio entre min_val y max_val (incluidos)."""
    # randrange no incluye el max, asi que sumamos 1
    return float(random.randrange(int(min_val), int(max_val) + 1))

def native_clear_screen():
    """Limpia la terminal. (Ahora redundante, pero se mantiene)."""
    # 'nt' es para Windows, 'posix' es para Mac/Linux
    os.system('cls' if os.name == 'nt' else 'clear')
    return None

def native_push_front(array, value):
    """Inserta un 'value' al inicio de un 'array' (lista)."""
    if not isinstance(array, list):
        raise Exception(u"push_front() solo funciona con arrays.")
    array.insert(0, value)
    return None

def native_pop_tail(array):
    """Quita y devuelve el ultimo elemento de un 'array' (lista)."""
    if not isinstance(array, list):
        raise Exception(u"pop_tail() solo funciona con arrays.")
    if len(array) == 0:
        raise Exception(u"pop_tail() no se puede usar en un array vacio.")
    return array.pop()


def native_get_key():
    """Obtiene una tecla presionada sin bloquear la ejecucion."""
    try:
        # --- Logica para Windows ---
        if msvcrt.kbhit():
            # Lee la tecla presionada y la devuelve como string
            return msvcrt.getch().decode('utf-8')
        return None  # No se presiono tecla

    except NameError:
        # --- Logica para Mac/Linux ---
        # Comprueba si hay datos listos para leer en 'sys.stdin'
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            # Lee un solo caracter
            # (Requiere configurar la terminal)
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        return None  # No se presiono tecla

def native_draw_grid(pantalla, constantes, score):
    """ Simula el Motor Gráfico: Limpia la terminal y dibuja el estado del juego."""
    
    import os
    import sys
    os.system('cls' if os.name == 'nt' else 'clear') 

    # 1. Obtener constantes (Dimensiones y valores clave)
    try:
        ALTO = int(constantes.fields.get(u'ALTO', 20.0))
        ANCHO = int(constantes.fields.get(u'ANCHO', 10.0))
        VACIO = constantes.fields.get(u'VACIO', 0.0)
    except:
        ALTO, ANCHO = len(pantalla), len(pantalla[0]) if pantalla else (20, 10)
        VACIO = 0.0
    
    
    # --- Detección del Juego y Configuración Dinámica ---
    is_snake = u'SERPIENTE' in constantes.fields

    if is_snake:
        JUEGO_TITULO = u"Retro Brik: SNAKE POWERUPS" 
        CONTROLES_A = u"W / S : Arriba / Abajo"
        CONTROLES_B = u"A / D : Izq / Der"
        
        # Mapeo de símbolos para Snake Avanzado
        SERPIENTE = constantes.fields.get(u'SERPIENTE', 1.0)
        COMIDA = constantes.fields.get(u'COMIDA_NORMAL', 2.0)
        CONGELADORA = constantes.fields.get(u'MOSCA_CONGELADORA', 3.0)
        FANTASMA = constantes.fields.get(u'MOSCA_FANTASMA', 4.0)
        MONEDA = constantes.fields.get(u'MONEDA_ORO', 5.0)
        OBSTACULO = constantes.fields.get(u'OBSTACULO', 6.0)
        
        PIXEL_MAP = {
            VACIO: u" .",
            SERPIENTE: u" #",
            COMIDA: u" @",        # Comida Normal
            CONGELADORA: u" C",   # Mosca Congeladora (C=Celeste)
            FANTASMA: u" F",      # Mosca Fantasma (F=Fantasma)
            MONEDA: u" $",        # Moneda de Oro
            OBSTACULO: u" X",     # Obstáculo
        }
    else:
        # Asumimos Tetris (Configuración anterior)
        JUEGO_TITULO = u"Retro Brik: TETRIS" 
        CONTROLES_A = u"A / D : Mover Pieza"
        CONTROLES_B = u"S : Caída Rápida"
        
        PIEZA = constantes.fields.get(u'PIEZA', 1.0)
        FIJO = constantes.fields.get(u'FIJO', 2.0)
        PIXEL_MAP = {
            VACIO: u" .",
            PIEZA: u"##", 
            FIJO: u"[]",  
        }
    
    PARTICIPANTE = u"David Delgado, Maria J. Gil"
    
    # 2. Construir el buffer de pantalla (La lógica de dibujado es la misma)
    ANCHO_TOTAL = ANCHO * 2 + 4
    borde_h = u"+" + u"-" * (ANCHO_TOTAL - 2) + u"+\n"
    buffer_pantalla = [borde_h]
    
    for y in range(ALTO):
        linea = u"|"
        for x in range(ANCHO):
            celda = pantalla[y][x]
            celda_key = celda if isinstance(celda, (float, int)) else VACIO
            linea += PIXEL_MAP.get(celda_key, u"??") 
        linea += u"|"
        
        # ... (Lógica de panel lateral) ...
        if y == 0: linea += u"   ====================="
        elif y == 1: 
             espacio_titulo = (21 - len(JUEGO_TITULO)) / 2 
             linea += u"   " + u" " * int(espacio_titulo) + JUEGO_TITULO
        elif y == 2: linea += u"   ====================="
        elif y == 4: linea += u"   [ PUNTUACIÓN ]"
        elif y == 5: linea += u"   Score: " + unicode(int(score))
        elif y == 7: linea += u"   [ CONTROLES ]"
        elif y == 8: linea += u"   " + CONTROLES_A
        elif y == 9: linea += u"   " + CONTROLES_B
        elif y == 11: linea += u"   [ AUTOR ]"
        elif y == 12: linea += u"   " + PARTICIPANTE
        
        buffer_pantalla.append(linea + u"\n")
        
    buffer_pantalla.append(borde_h)
    sys.stdout.write(u"".join(buffer_pantalla))
    
    return None

class Environment(object):
    def __init__(self):
        # El "cerebro" es un diccionario para guardar variables
        self.variables = {}
        self.declare(u"len", BrikNativeFunction(native_len), is_constant=True)
        self.declare(u"sleep", BrikNativeFunction(native_sleep), is_constant=True)
        self.declare(u"rand", BrikNativeFunction(native_rand), is_constant=True)
        self.declare(u"clear_screen", BrikNativeFunction(native_clear_screen), is_constant=True)
        self.declare(u"push_front", BrikNativeFunction(native_push_front), is_constant=True)
        self.declare(u"pop_tail", BrikNativeFunction(native_pop_tail), is_constant=True)
        self.declare(u"get_key", BrikNativeFunction(native_get_key), is_constant=True)
        self.declare(u"draw_grid", BrikNativeFunction(native_draw_grid), is_constant=True) 

        self.declare(u"true", True, is_constant=True)
        self.declare(u"false", False, is_constant=True)

    def declare(self, name, value, is_constant):
        """Define una nueva variable (let o const)"""
        # if name in self.variables:
        #    raise Exception(u"Variable ya definida: " + name)

        # (Mas tarde guardaremos 'is_constant' para
        #  prevenir re-asignaciones a 'const')
        self.variables[name] = value
        return value

    def get(self, name):
        """Obtiene el valor de una variable"""
        if name not in self.variables:
            raise Exception(u"Variable no definida: " + name)
        return self.variables[name]

    def assign(self, name, value):
        """Asigna un nuevo valor a una variable ya existente"""
        if name not in self.variables:
            raise Exception(u"Asignacion a variable no definida: " + name)

        # (Mas tarde aqui puedes comprobar si es 'const')

        self.variables[name] = value
        return value