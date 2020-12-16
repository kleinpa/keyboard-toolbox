text = """
#pragma once
#include "config_common.h"

/* USB Device descriptor parameter */
#define VENDOR_ID       0xDEAF
#define PRODUCT_ID      0x0913
#define DEVICE_VER      0x0001
#define MANUFACTURER    imchipwood
#define PRODUCT         dumbpad
#define DESCRIPTION     4x4 macro/numpad with rotary encoder


/*
 * Keyboard Matrix Assignments
 *
 * Change this to how you wired your keyboard
 * COLS: AVR pins used for columns, left to right
 * ROWS: AVR pins used for rows, top to bottom
 * DIODE_DIRECTION: COL2ROW = COL = Anode (+), ROW = Cathode (-, marked on diode)
 *                  ROW2COL = ROW = Anode (+), COL = Cathode (-, marked on diode)
 *
*/
#define MATRIX_ROWS 4
#define MATRIX_COLS 5
#define MATRIX_ROW_PINS { F4, F5, F6, F7 }
#define MATRIX_COL_PINS { C6, D7, E6, B4, B5 }
#define UNUSED_PINS

/* COL2ROW, ROW2COL*/
#define DIODE_DIRECTION COL2ROW

/* Rotary encoder */
#define ENCODERS_PAD_A { D0 }
#define ENCODERS_PAD_B { D4 }

/* LED layer indicators */
#define LAYER_INDICATOR_LED_0 B3
#define LAYER_INDICATOR_LED_1 B1

/* Bootmagic - hold down rotary encoder pushbutton while plugging in to enter bootloader */
#define BOOTMAGIC_LITE_ROW 3
#define BOOTMAGIC_LITE_COLUMN 0


/* Debounce reduces chatter (unintended double-presses) - set 0 if debouncing is not needed */
#define DEBOUNCE 5

/* define if matrix has ghost (lacks anti-ghosting diodes) */
//#define MATRIX_HAS_GHOST

/* number of backlight levels */

/* Mechanical locking support. Use KC_LCAP, KC_LNUM or KC_LSCR instead in keymap */
//#define LOCKING_SUPPORT_ENABLE
/* Locking resynchronize hack */
//#define LOCKING_RESYNC_ENABLE
"""


def make_qmk_header(kb):
    # need key -> matrix position
    # need key -> x.y position
    # are they related?

    return text
