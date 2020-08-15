"""
TODO
Random puzzle generator
Rework victory screen
Add new buttons
"""



import argparse
from tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM

BOARDS = ['debug', 'easy', 'hard', 'clean']  # Available sudoku boards
BoardPixelCNT = 20  # Pixels around the board
SIDE = 50  # Width of every board cell.
BoardWidth = BoardPixelCNT * 2 + SIDE * 9
BoardHeight = BoardPixelCNT * 2 + SIDE * 9  # Width and height of the whole board


class SudokuError(Exception):
    pass


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--board",
                            help="Desired board name",
                            type=str,
                            choices=BOARDS,
                            required=True)

    # Creates a dictionary of keys = argument flag, and value = argument
    args = vars(arg_parser.parse_args())
    return args['board']


class UserInterface(Frame):
    def __init__(self, parent, game):
        self.game = game
        Frame.__init__(self, parent)
        self.parent = parent

        self.row, self.col = -1, -1

        self.__initUI()

    def __initUI(self):
        self.parent.title("Sudoku")
        self.pack(fill=BOTH)
        self.canvas = Canvas(self,
                             width=BoardWidth,
                             height=BoardHeight)
        self.canvas.pack(fill=BOTH, side=TOP)
        clear_button = Button(self,
                              text="Clear answers",
                              command=self.__clear_board)
        # easy_mode_button = Button(self,
        #                           text="Easy Mode",
        #                           command=self.__clear_board)
        # hard_mode_button = Button(self,
        #                           text="Hard Mode",
        #                           command=self.__draw_blank())
        # free_mode_button = Button(self,
        #                           text="Free Play Mode",
        #                           command=self.__draw_sudoku())

        """
        For future development
        """
        clear_button.pack(fill=BOTH, side=BOTTOM)
        # easy_mode_button.pack(fill=BOTH)
        # hard_mode_button.pack(fill=BOTH)
        # free_mode_button.pack(fill=BOTH, side=BOTTOM)

        self.pack()
        self.__draw_grid()
        self.__draw_sudoku()

        self.canvas.bind('<Return>', self.game.check_win())
        self.canvas.bind("<Button-1>", self.__cell_active)
        self.canvas.bind("<Key>", self.__key_event)


    def __draw_grid(self):
        for i in range(10):
            color = "blue" if i % 3 == 0 else "gray"

            x0 = BoardPixelCNT + i * SIDE
            y0 = BoardPixelCNT
            x1 = BoardPixelCNT + i * SIDE
            y1 = BoardHeight - BoardPixelCNT
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = BoardPixelCNT
            y0 = BoardPixelCNT + i * SIDE
            x1 = BoardWidth - BoardPixelCNT
            y1 = BoardPixelCNT + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def __draw_sudoku(self):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                answer = self.game.puzzle[i][j]
                if answer != 0:
                    x = BoardPixelCNT + j * SIDE + SIDE / 2
                    y = BoardPixelCNT + i * SIDE + SIDE / 2
                    original = self.game.start_puzzle[i][j]
                    color = "black" if answer == original else "blue"
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers", fill=color
                    )

    # def __draw_blank(self):
    #     self.canvas.delete("numbers")
    #     for i in range(9):
    #         for j in range(9):
    #             answer = 0
    #             if answer != 0:
    #                 x = BoardPixelCNT + j * SIDE + SIDE / 2
    #                 y = BoardPixelCNT + i * SIDE + SIDE / 2
    #                 original = self.game.start_puzzle[i][j]
    #                 color = "black" if answer == original else "blue"
    #                 self.canvas.create_text(
    #                     x, y, text=answer, tags="numbers", fill=color
    #                 )

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = BoardPixelCNT + self.col * SIDE + 1
            y0 = BoardPixelCNT + self.row * SIDE + 1
            x1 = BoardPixelCNT + (self.col + 1) * SIDE - 1
            y1 = BoardPixelCNT + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor"
            )

    def __draw_victory(self):
        # create a oval (which will be a circle)
        x0 = y0 = BoardPixelCNT + SIDE * 2
        x1 = y1 = BoardPixelCNT + SIDE * 7
        self.canvas.create_rectangle(
            x0, y0, x1, y1,
            tags="victory", fill="dark orange", outline="orange"
        )
        # create text
        x = y = BoardPixelCNT + 4 * SIDE + SIDE / 2
        self.canvas.create_text(
            x, y,
            text="Victory!", tags="victory",
            fill="white", font=("Arial", 32)
        )

    def __cell_active(self, event):
        if self.game.game_over:
            return
        x, y = event.x, event.y
        if (BoardPixelCNT < x < BoardWidth - BoardPixelCNT and BoardPixelCNT < y < BoardHeight - BoardPixelCNT):
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = (y - BoardPixelCNT) / SIDE, (x - BoardPixelCNT) / SIDE
            row=int(row)
            col=int(col)

            # if cell was selected already - deselect it
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            elif self.game.puzzle[row][col] == 0:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1

        self.__draw_cursor()

    def __key_event(self, event):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.game.puzzle[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.__draw_sudoku()
            self.__draw_cursor()
            if self.game.check_win():
                self.__draw_victory()

    def __clear_board(self):
        self.game.start()
        self.canvas.delete("victory")
        self.__draw_sudoku()


class SudokuBoard(object):
    def __init__(self, board_file):
        self.board = self.__create_board(board_file)

    def __create_board(self, board_file):
        board = []
        for line in board_file:
            line = line.strip()
            if len(line) != 9:
                raise SudokuError(
                )
            board.append([])

            for c in line:
                if not c.isdigit():
                    raise SudokuError(
                    )
                board[-1].append(int(c))

        if len(board) != 9:
            raise SudokuError("This board isn't up to code!")
        return board


class SudokuGame(object):
    def __init__(self, board_file):
        self.board_file = board_file
        self.start_puzzle = SudokuBoard(board_file).board

    def start(self):
        self.game_over = False
        self.puzzle = []
        for i in range(9):
            self.puzzle.append([])
            for j in range(9):
                self.puzzle[i].append(self.start_puzzle[i][j])

    def check_win(self):
        for row in range(9):
            if not self.__check_row(row):
                return False
        for column in range(9):
            if not self.__check_col(column):
                return False
        for row in range(3):
            for column in range(3):
                if not self.__check_sq(row, column):
                    return False
        self.game_over = True
        return True

    def __check_block(self, block):
        return set(block) == set(range(1, 10))

    def __check_row(self, row):
        return self.__check_block(self.puzzle[row])

    def __check_col(self, column):
        return self.__check_block(
            [self.puzzle[row][column] for row in range(9)]
        )

    def __check_sq(self, row, column):
        return self.__check_block(
            [
                self.puzzle[r][c]
                for r in range(row * 3, (row + 1) * 3)
                for c in range(column * 3, (column + 1) * 3)
            ]
        )


if __name__ == '__main__':
    board_name = parse_arguments()

    with open('%s.sudoku' % board_name, 'r') as boards_file:
        game = SudokuGame(boards_file)
        game.start()

        root = Tk()
        UserInterface(root, game)
        root.resizable(False, False)
        root.geometry("%dx%d" % (BoardWidth, BoardHeight + 40))
        root.mainloop()