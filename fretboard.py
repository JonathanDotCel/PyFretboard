# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# github.com/JonathanDotCel

from functools import cache
import matplotlib.pyplot as plt

# Determines graph length (not number of frets)
# Isn't super important visually
FRETBOARD_LENGTH = 25

# Make things fit the screen a bit better
GRAPH_X_SCALE = 4
GRAPH_Y_SCALE = 12

# Semitones
# Since there's a one to many note->name relationship,
# let's just skip any fancy scale-aware lookup
TUNING_A = 0
TUNING_As = 1
TUNING_Bb = 1
TUNING_B = 2
TUNING_Bs = 3  # Accounting for lack of B#
TUNING_Cb = 2
TUNING_C = 3
TUNING_Cs = 4
TUNING_Db = 4
TUNING_D = 5
TUNING_Ds = 6
TUNING_Eb = 6
TUNING_E = 7
TUNING_Es = 8  # Accounting for lack of E#
TUNING_Fb = 7
TUNING_F = 8
TUNING_Fs = 9
TUNING_Gb = 9
TUNING_G = 10
TUNING_Gs = 11

# E.g. F major and D minor
targetScale = TUNING_F

# Fretboard object
board = None

# 0-indexed semitone to friendly name
# TODO: solfa?


def Semi2Note(inSemi):
    return ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"][inSemi % 12]


# An array probs would've done the job
class String:
    def __init__(self, tuningOffset):
        self.tuningOffset = tuningOffset

# The fretboard with all the child strings


class Fretboard:

    def __init__(self):

        self.strings = []

        # as good a default as any
        self.scale = TUNING_E
        self.numFrets = 24

        # layout
        # factor in the nut and a 'fake' open fret before that
        self.linesToDraw = 0
        self.stringSpacing = 0
        self.bottom = 0
        self.top = 0
        self.fretPositions = []

        # Some stuff that needs precalced
        self.__CalcFretPositions()

        # Render opts
        self.drawPenta = True
        self.drawBlueNote = False
        self.drawOtherDiatonic = True
        self.drawHarmonicMinor = False

    def CheckInit(self):
        return len(self.strings) > 0

    # Precalc where each fret would be
    # Note: since e.g. 4 frets would require 5 bits of fret wire
    #       we'll also want a 6th 'virual' fret to make drawing the
    #       open string stuff easier
    def __CalcFretPositions(self):

        # http://www.buildyourguitar.com/resources/tips/fretdist.htm

        cachedPositions = []

        fretLength = 0
        remainingScaleLength = FRETBOARD_LENGTH

        xPos = 0

        self.linesToDraw = self.numFrets + 2

        for fretId in range(self.linesToDraw):

            xPos += fretLength * GRAPH_X_SCALE
            cachedPositions.append(xPos)

            #print("Fret {} xpos is {}".format(fretId, xPos))

            if fretId == 0:
                # fake fret for open strings
                # TODO: could maybe do to be a multiple of the board scales
                fretLength = 0.6
            else:
                fretLength = remainingScaleLength / 17.817
                remainingScaleLength -= fretLength

        self.fretPositions = cachedPositions

    # Register a string for which you've already picked a tuning
    # Go nuts
    def AddString(self, inString):
        self.strings.append(inString)

        self.stringSpacing = (GRAPH_Y_SCALE / (len(self.strings)+1))

        # would be weird having a full string space between the string
        # and the edge of the fretboard
        self.bottom = 0 + (self.stringSpacing / 2)
        self.top = GRAPH_Y_SCALE - (self.stringSpacing / 2)

    # Where to place the finger dots
    def __DotX(self, xIndex):

        if not self.CheckInit():
            return 0

        # Bad finger pos, but easier to read!
        xOffset = (self.fretPositions[xIndex] +
                   self.fretPositions[xIndex+1]) * 0.5
        return xOffset

    # Where to place the finger dots
    def __DotY(self, stringId):

        if not self.CheckInit():
            return 0

        # E.g. 6 strings split the Y height into 7 positions
        # just as e.g. 1 line splits a thing in 2
        divisor = len(self.strings) + 1
        yOffset = (GRAPH_Y_SCALE / divisor) * (stringId+1)

        return yOffset

    # Does a thing
    def DrawFrets(self):

        if not self.CheckInit():
            print("No strings for DrawFrets()\n")
            return

        for fretId in range(self.linesToDraw):

            xPos = self.fretPositions[fretId]

            # We want it to count towards the graph's overall
            # bounding box, but not necessarily draw
            # Could set alpha to 0, etc
            lineWidth = 2.5 if fretId > 0 else 0

            line = plt.Line2D((xPos, xPos), (self.bottom, self.top),
                              lineWidth, markerfacecolor="r")
            plt.gca().add_line(line)

    # TODO: fix the draw order
    def DrawStrings(self):

        if not self.CheckInit():
            print("no strings...\n")
            return

        for stringId in range(len(self.strings)):

            divisor = len(self.strings) + 1
            yOffset = (GRAPH_Y_SCALE / divisor) * (stringId+1)

            line = plt.Line2D((0, self.fretPositions[-1]), (yOffset, yOffset),
                              1, markerfacecolor="black")
            plt.gca().add_line(line)

        # fill in the top and bottom
        line = plt.Line2D(
            (0, self.fretPositions[-1]), (self.bottom, self.bottom), 1, markerfacecolor="black", alpha=0.5)
        plt.gca().add_line(line)
        line = plt.Line2D(
            (0, self.fretPositions[-1]), (self.top, self.top), 1, markerfacecolor="black", alpha=0.5)
        plt.gca().add_line(line)

    # I wanted to get fancy, maybe fill in some sin() graphs, etc
    # but it's already slow enough
    def DrawFretMarkers(self):

        if not self.CheckInit():
            print("no strings...\n")

        # include the open string + e.g. 12 frets
        dotsPerString = self.numFrets + 1

        dottedFrets = [0, 3, 5, 7, 9]

        for frettyBit in range(dotsPerString):

            mod12 = frettyBit % 12

            if not mod12 in dottedFrets:
                continue

            # Technically an octave of frets 12,24, etc
            # But we don't want dots on open strings...
            if (frettyBit == 0):
                continue

            fretStart = self.fretPositions[frettyBit]
            fretEnd = self.fretPositions[frettyBit+1]

            fretLength = fretEnd - fretStart

            if mod12 == 0:
                # double dot
                w = fretLength * 0.6
                h = GRAPH_Y_SCALE * 0.9
                x = fretStart + (fretLength * 0.2)
                y = GRAPH_Y_SCALE * 0.05

                rect = plt.Rectangle((x, y), w, h, alpha=0.2)
                plt.gca().add_patch(rect)

            else:
                # single dot
                w = fretLength * 0.9
                h = GRAPH_Y_SCALE * 0.1
                x = fretStart + (fretLength * 0.05)
                y = GRAPH_Y_SCALE * 0.45

                rect = plt.Rectangle((x, y), w, h, alpha=0.2)
                plt.gca().add_patch(rect)

            # wee black circle
            x = fretStart + (fretLength * 0.5)
            y = - (GRAPH_Y_SCALE / len(self.strings)) * 0.5
            circle = plt.Circle((x, y), radius=0.6, fc="black", alpha=0.2)
            plt.gca().add_patch(circle)

    # Actually render out the scale's dots
    # based on the current config
    def DrawDots(self):

        if not self.CheckInit():
            print("no strings...\n")

        # include the open string + e.g. 12 frets
        dotsPerString = self.numFrets + 1

        for stringId in range(len(self.strings)):

            yPos = self.__DotY(stringId)

            for frettyBit in range(dotsPerString):

                xPos = self.__DotX(frettyBit)

                stringOffset = self.strings[stringId].tuningOffset

                actualNote = (frettyBit + stringOffset - self.scale) % 12

                noteColor = None

                # Major root
                if actualNote == 0:
                    noteColor = "green"

                # Relative minor
                if actualNote == 9:
                    noteColor = "red"

                # Pentatonic maj/min (from a Maj scale frame of reference)
                # 0 and 3 already included
                if self.drawPenta and actualNote in [2, 4, 7]:
                    noteColor = "black"

                # The bluesy blue note
                if self.drawBlueNote and actualNote == 3:
                    noteColor = "blue"

                # Perfect 4th and Maj 7th missing
                # Or, I guess 2nd and 6th in relative minor
                if self.drawOtherDiatonic and actualNote in [5, 11]:
                    noteColor = "gray"

                # Easily the best note
                # Sharp 7th for harmonic minor
                if self.drawHarmonicMinor and actualNote == 8:
                    noteColor = "orange"

                if noteColor is not None:

                    circle = plt.Circle((xPos, yPos), radius=0.6, fc=noteColor)
                    plt.gca().add_patch(circle)

    # Draws the frets, markers, dots, strings, etc
    # It's not the job of this function to ensure
    # matplotlib is ready to redraw!
    def Draw(self, inScale):

        self.scale = inScale

        self.DrawFrets()
        self.DrawFretMarkers()
        self.DrawStrings()
        self.DrawDots()

        scaleString = Semi2Note(self.scale)
        relativeMinorString = Semi2Note(self.scale - 3)
        plt.title("Root = {}Maj/{}Min (up/down)  Frets={} (left/right) \n Penta/Dia={} (1) | Blue/Flat5={} (2) | Harmonic Minor={} (3)".format(
            scaleString, relativeMinorString, self.numFrets, self.drawOtherDiatonic, self.drawBlueNote, self.drawHarmonicMinor))

    def Redraw(self):
        pass

    # Callback from the main matplotlib window
    def onKeyPressed(self, event):

        #print( "Key: {}".format( event.key ) )

        # 1,2,3 to toggle opts
        # Could be worth tidying up if more options are added
        if (event.key == "1"):
            self.drawOtherDiatonic = not self.drawOtherDiatonic
        if (event.key == "2"):
            self.drawBlueNote = not self.drawBlueNote
        if (event.key == "3"):
            self.drawHarmonicMinor = not self.drawHarmonicMinor

        # Since stuff like "S" is already bound...
        if (event.key == "up"):
            self.scale += 1
        if (event.key == "down"):
            self.scale -= 1

        if (event.key == "left"):
            self.numFrets -= 1
            if self.numFrets < 1:
                self.numFrets = 1
            self.__CalcFretPositions()

        if (event.key == "right"):
            self.numFrets += 1
            self.__CalcFretPositions()

        plt.gca().clear()
        plt.axis("scaled")
        self.Draw(self.scale)
        plt.draw()


# plt.xlim(0, 8), plt.ylim(-2, 8)

# Start witht he chonky ones
board = Fretboard()
board.AddString(String(TUNING_E))
board.AddString(String(TUNING_A))
board.AddString(String(TUNING_D))
board.AddString(String(TUNING_G))
board.AddString(String(TUNING_B))
board.AddString(String(TUNING_E))

plt.axes()

board.Draw(targetScale)

plt.axis("scaled")

canvas = plt.gca().figure.canvas
canvas.mpl_connect('key_press_event', board.onKeyPressed)

plt.show()
