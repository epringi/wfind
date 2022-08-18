#!/usr/bin/env python3

import signal, sys, time, os, secrets, shutil, glob, random, re, select, curses

# There's an ESC key delay by default, so let's put that to 0
os.environ.setdefault('ESCDELAY', '0')
# Remove the pygame promotional text when the library is loaded...
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# define the default (min) board size
size=4

# instead of kacking out, check the terminal size
if shutil.get_terminal_size()[0]<21 or shutil.get_terminal_size()[1]<21:
  print("AW, terminal must be at least 21x21 to play the boggle. :(")
  exit()

# curses init stuff
screen=curses.initscr()
screen.keypad(True)
curses.noecho()
curses.cbreak()
#boardwin.keypad(True)
curses.start_color()
curses.use_default_colors()
curses.curs_set(0)
#wordlist=curses.initscr()
#wordlist.keypad(True)
wordlist=curses.newwin(curses.LINES, 28, 0, curses.COLS-28)
wordlist.keypad(True)
boardwin=curses.newwin(curses.LINES, curses.COLS-28, 0, 0)
boardwin.keypad(True)

for ln in range(curses.LINES):
  wordlist.addstr(ln, 0, "|")
wordlist.refresh()

# sigint is ok
def signal_handler(sig, frame):
  curses.nocbreak()
  screen.keypad(False)
  wordlist.keypad(False)
  boardwin.keypad(False)
  curses.echo()
  curses.endwin()
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# in case we run if from elsewhere, make sure we know where this is in the fs
wd=os.path.dirname(os.path.realpath(__file__))

(bymid, bxmid)=boardwin.getmaxyx()
bxmid=int(bxmid/2)
bymid=int(bymid/2)

alphabet=[ 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'QU', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z' ]
alphaweights=[ 8.12, 1.49, 2.71, 4.32, 12.02, 2.30, 2.03, 5.92, 7.31, 0.10, 0.69, 3.98, 2.61, 6.95, 7.68, 1.82, 0.11, 6.02, 6.28, 9.10, 2.88, 1.11, 2.09, 0.17, 2.11, 0.07 ]

'''E 	21912
T 	16587
A 	14810
O 	14003
I 	13318
N 	12666
S 	11450
R 	10977
H 	10795
D 	7874
L 	7253
U 	5246
C 	4943
M 	4761
F 	4200
Y 	3853
W 	3819
G 	3693
P 	3316
B 	2715
V 	2019
K 	1257
X 	315
Q 	205
J 	188
Z 	128'''


'''use percentage to determine how many can be on  the board. check how many have been chosen
E 	21912 	  	E 	12.02
T 	16587 	  	T 	9.10
A 	14810 	  	A 	8.12
O 	14003 	  	O 	7.68
I 	13318 	  	I 	7.31
N 	12666 	  	N 	6.95
S 	11450 	  	S 	6.28
R 	10977 	  	R 	6.02
H 	10795 	  	H 	5.92
D 	7874 	  	D 	4.32
L 	7253 	  	L 	3.98
U 	5246 	  	U 	2.88
C 	4943 	  	C 	2.71
M 	4761 	  	M 	2.61
F 	4200 	  	F 	2.30
Y 	3853 	  	Y 	2.11
W 	3819 	  	W 	2.09
G 	3693 	  	G 	2.03
P 	3316 	  	P 	1.82
B 	2715 	  	B 	1.49
V 	2019 	  	V 	1.11
K 	1257 	  	K 	0.69
X 	315 	  	X 	0.17
Q 	205 	  	Q 	0.11
J 	188 	  	J 	0.10
Z 	128 	  	Z 	0.07'''

f=open("words", 'r')
words=f.readlines()
words = [item.strip() for item in words]

#board=[getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet(), getlet()]
board=random.choices(alphabet, weights=alphaweights, k=25)

# I wanted to call this var neighbours, but didn't want to have to keep typing it out...
pals=[
  [1,5,6], [0,5,6,7,2], [1,6,7,8,3], [2,7,8,9,4], [3,8,9],
  [0,1,6,10,11], [0,1,2,5,7,10,11,12], [1,2,3,6,8,11,12,13], [2,3,4,7,9,12,13,14], [3,4,8,13,14],
  [5,6,11,15,16], [5,6,7,10,12,15,16,17], [6,7,8,11,13,16,17,18], [7,8,9,12,14,17,18,19], [8,9,13,18,19],
  [10,11,16,20,21], [10,11,12,15,17,20,21,22], [11,12,13,16,18,21,22,23], [12,13,14,17,19,22,23,24], [13,14,18,23,24],
  [15,16,21], [15,16,17,20,22], [16,17,18,21,23], [17,18,19,22,24], [18,19,23]
]

used=[]

tried=0

newlist=[]
boardlist=[]
sofar=""
progressbar="•°°•••°°•••°°••"
progressbar="tABuWiZLyzJPbrRdBkVhcAUogbZaZSNFqRBAaDsSGSWudmKSrCErNDwRHRfiZuKC"
progressbar="t•A•B•u•W•i•Z•L•y•z•J•P•b•r•R•d•B•k•V•h•c•A•U•o•g•b•Z•a•Z•S•N•F•q•R•B•A•a•D•s•S•G•S•W•u•d•m•K•S•r•C•E•r•N•D•w•R•H•R•f•i•Z•u•K•C•"

#build_list()
boardlist=['NET', 'NERD', 'NERDY', 'NTH', 'ERT', 'ERG', 'RIB', 'BRR', 'BIRR', 'BIRD', 'TEN', 'TERN', 'RENT', 'GENT', 'GET', 'GRE', 'RYA', 'LULL', 'LULLS', 'HULL','HULLS', 'DREG', 'DRY', 'DRYAD', 'DRYADS', 'DYAD', 'DYADS', 'YANG', 'LOLL', 'LOLLS', 'GAY', 'GAD', 'GADS', 'GAN', 'ADS', 'AND', 'LOLLY', 'OLD', 'OLDY', 'SLY',
'SOU', 'SOUL', 'SOL', 'SOLD', 'DAY', 'DAG', 'DAGS', 'DANG', 'DANGS', 'NAY', 'NAG', 'NAGS', 'NAD', 'NADS']
board=['N','E','N','R','B','T','R','G','R','I','L','H','D','Y','Y','U','L','L','G','A','L','O','S','D','N']
draw_board()


def draw_board():
  posx=bxmid-16
  posy=bymid-11

  if posx<0:
    posx=0
  if posy<0:
    posy=0

  boardwin.addstr(posy, posx, "_".rjust(31, "_"))
  letter=0
  for inc in range(1,16):
    if ((inc-2)%3==0):
      boardwin.addstr(posy+inc, posx, "|  "+board[letter].ljust(2)+" |  "+board[letter+1].ljust(2)+" |  "+board[letter+2].ljust(2)+" |  "+board[letter+3].ljust(2)+" |  "+board[letter+4].ljust(2)+" |")
      letter=letter+5
    elif (inc%3)!=0:
      boardwin.addstr(posy+inc, posx, "|     |     |     |     |     |")
    else:
      boardwin.addstr(posy+inc, posx, "|_____|_____|_____|_____|_____|")
  boardwin.refresh()


def find_path(slet):
  global used
  global sofar
  global newlist
  global boardlist
  global progressbar

  if (len(used)%2)==0:
    progressbar=progressbar[1:]+progressbar[0:1]
    boardwin.addstr(bymid+1, bxmid-11, progressbar[0:15])
    boardwin.refresh()

  for idx, val in enumerate(pals[slet]):
    if val not in used:
      r=re.compile("^"+sofar+board[val])
      if len(used)>1 and len(newlist)>0:
        newlist = list(filter(r.match, newlist))
      else:
        newlist = list(filter(r.match, words))
      if len(newlist)>0:
        sofar=sofar+board[val]
        used.append(val)
        slet=val
        # if what we found so far is a whole word in newlist, add it to the list of words in the board
        if sofar in newlist and sofar not in boardlist:
          boardlist.append(sofar)

        find_path(slet)
        newlist=[]
        used=used[0:-1]
        sofar=sofar[0:-1]
        slet=used[-1]


def build_list():
  global used
  global tried
  global sofar
  global newlist
  global boardlist
  oslet=0
  sofar=board[oslet]
  used.append(0)

  boardwin.addstr(bymid-1, bxmid-11, "Building  board")
  boardwin.addstr(bymid+1, bxmid-11, progressbar[0:15])
  boardwin.refresh()

  while tried<25:
    used=[]
    used.append(oslet)
    sofar=board[oslet]
    newlist=[]
    find_path(oslet)
    oslet=oslet+1
    tried=tried+1



def valid_letter(char):
  global used
  global pals

  chars=[i for i, e in enumerate(board) if e == char]

  if char not in board:
    return False
  elif len(used)==0:
    return chars[0]

  for idx in chars:
    for idx2 in pals[used[-1]]:
      if idx==idx2 and idx not in used:
        return idx

  word=""
  for idx in used:
    word=word+board[idx]
  word=word+char

  wordidx=[]
  for letter in word:
    lidx=[i for i, e in enumerate(board) if e == letter]
    wordidx.append(list(lidx))

  letterpals=[]
  for idx, letter in enumerate(wordidx):
    lpals=[]
    for idx2 in letter:
      #lpals.extend(pals[idx])
      paldict={idx2: pals[idx2]}
      letterpals.append(paldict)
    #letterpals.append(lpals)

  boardwin.addstr(str(letterpals))
  boardwin.refresh()
  droppped=[]
  for idx, letter in enumerate(wordidx):
    if idx<len(wordidx)-1:
      for idx2, place in enumerate(letter):
        for palsidx in letterpals[idx+1]: #added
        #if place not in letterpals[idx+1]:
          if place not in letterpals[idx+1][palsidx]:
            del wordidx[idx][idx2]
            del wordidx[idx+1][palsidx]
    elif idx!=0:
      for idx2, place in enumerate(letter):
        for palsidx in letterpals[idx-1]: #added
        #if place not in letterpals[idx-1]:
          if place not in palsidx:
            del wordidx[idx][idx2]
            del wordidx[idx-1][palsidx]

  newused=[]
  for letter in wordidx:
    if len(letter)==0:
      return False
    else:
      newused.append(letter[0])

  for item in used:
    deselect_letter()

  char=newused[-1]

  for item in newused[0:-1]:
    select_letter("", item)

  return char



def select_letter(char, charidx=None):
  global used
  global board

  if charidx==None:
    charidx=valid_letter(char)

  posx=(bxmid - 16) + 3 + ((charidx-(int(charidx/5)*5))*6)
  posy=(bymid-11) + 2 + (int(charidx/5)*3)

  used.append(charidx)
  boardwin.addstr(posy, posx, board[charidx], curses.A_BOLD)
  #boardwin.addstr(1,0,str(used).ljust(3, " "))
  boardwin.refresh()

def deselect_letter():
  global used
  global board

  charidx=used[-1]
  posx=(bxmid - 16) + 3 + ((charidx-(int(charidx/5)*5))*6)
  posy=(bymid-11) + 2 + (int(charidx/5)*3)

  boardwin.addstr(posy, posx, board[charidx])
  used=used[0:-1]
  #boardwin.addstr(1,0,str(used).ljust(3, " "))
  boardwin.refresh()

def valid_word():
  global used
  global board
  global boardlist

  word=""

  for letter in used:
    word=word+board[letter]

  if word in boardlist:
    return word
  else:
    word_alert()
    return False

def add_word(word):
  global found
  global used
  global board

  found.append(valid_word())
  for idx in used:
    posx=(bxmid - 16) + 3 + ((idx-(int(idx/5)*5))*6)
    posy=(bymid-11) + 2 + (int(idx/5)*3)
    boardwin.addstr(posy, posx, board[idx])

  boardwin.refresh()
  found.sort()
  posy=0
  posx=1
  for idx, word in enumerate(found):
    #if idx=curses.LINES-1:
    if idx==curses.LINES:
      posy=0
      posx=16
    wordlist.addstr(posy, posx, word)
    posy=posy+1
  wordlist.refresh()
  used=[]

def word_alert():
  global used
  global board

  word=""

  for letter in used:
    word=word+board[letter]

  line=word+" is NOT in the dictionary!"
  posx=bxmid-int(len(line)/2)
  posy=bymid+7
  boardwin.addstr(posy, posx, line)
  boardwin.refresh()


found=[]
used=[]

key=23
#q = 113
#u=117
while key!=27:
  key=boardwin.getch()
  boardwin.addstr(bymid+7, bxmid-20, " ".ljust(40, " "))
  #boardwin.addstr(0,0,chr(key).ljust(3, " ")+str(key).ljust(3, " "))
  #boardwin.addstr(2,0," ".ljust(40, " "))
  #boardwin.addstr(3,0," ".ljust(40, " "))
  #boardwin.addstr(4,0," ".ljust(40, " "))
  #boardwin.addstr(5,0," ".ljust(40, " "))
  boardwin.refresh()
  char=chr(key).upper()

  if key<=122 and key>=97:
    #boardwin.addstr(2,0,"is letter")
    #boardwin.refresh()
    #if chr(key) in board and ((len(used)>0 and valid_letter(chr(key))) or len(used)==0):
    if char in board:
      #boardwin.addstr(3,0,"is in board")
      #boardwin.refresh()
      if len(used)>0 and valid_letter(char):
        #boardwin.addstr(4,0,"used is bigger than 0 and it's a valid letter")
        #boardwin.refresh()
        select_letter(char)
      if len(used)==0:
        #boardwin.addstr(5,0,"used is zero")
        #boardwin.refresh()
        select_letter(char)
    #else:
    #  boardwin.addstr(3,0,"is NOT in board")
    #  boardwin.refresh()

  if key==263 and len(used)>0:
    deselect_letter()

  if key==10 and len(used)>0:
    if valid_word():
      add_word(valid_word())



curses.nocbreak()
screen.keypad(False)
wordlist.keypad(False)
boardwin.keypad(False)
curses.echo()
curses.endwin()
sys.exit(0)
