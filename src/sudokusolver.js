var table = document.getElementById('game-grid');
var cells = table.getElementsByTagName('td');
var solution = document.querySelector('#solve-puzzle');
var newGrid = document.querySelector('#new-game');
let running = false;
let board = [...Array(9)].map(e => Array(9)); //Game grid
let canEditBoard = [...Array(9)].map(e => Array(9)); //Game grid with boolean values to check which squares are editable
let popup = document.getElementById("popup");

initializeSolution();

function initializeSolution() {
    for(var i = 0; i < cells.length; i++) {
        cells[i].onclick = function() {
            if(this.hasAttribute('data-clicked')) {
                return;
            }
            this.setAttribute('data-clicked', 'yes');
            this.setAttribute('data-text', this.innerHTML);

            var input = document.createElement('input');
            input.setAttribute('type', 'number');
            input.setAttribute('min', 1);
            input.setAttribute('max', 9);
            input.value = this.innerHTML;
            input.style.width = this.offsetWidth - (this.clientLeft * 2) + "px";
            input.style.height = this.offsetHeight - (this.clientTop * 2) + "px";
            input.style.border = "0px";
            input.style.fontFamily = "inherit";
            input.style.fontSize = "inherit";
            input.style.textAlign = "inherit";
            input.style.backgroundColor = "LightGoldenRodYellow";

            input.onblur = function() {
                var td = input.parentElement;
                var orig_text = input.parentElement.getAttribute('data-text');
                var current_text = this.value;

                if(orig_text != current_text) {
                    td.removeAttribute('data-clicked');
                    td.removeAttribute('data-text');
                    td.innerHTML = current_text;
                    td.style.cssText = 'padding: 5px';
                    console.log(orig_text + ' is changed to ' + current_text);
                } else {
                    td.removeAttribute('data-clicked');
                    td.removeAttribute('data-text');
                    td.innerHTML = orig_text;
                    td.style.cssText = 'padding: 5px';
                    console.log('No changes made');
                }
            }

            input.addEventListener('keyup', function(event) {
                if(event.code == 'Enter') {
                    this.blur();
                }
            });

            this.innerHTML = '';
            this.style.cssText = 'padding: 0px 0px';
            this.append(input);
            this.firstElementChild.select();
        }
    }
}

//Converts the table into a two dimensional array
function tableToArray() {
    console.log(cells);

    var currentCell = 0;
    //Check if square is populated, if not then populate
    for(let i = 0; i < board.length; i++) {
        for(let j = 0; j < board.length; j++) {
            if(cells[currentCell].innerHTML == "") {
                board[i][j] = "";
            } else {
                board[i][j] = cells[currentCell].innerHTML;
            }

            if(board[i][j] != "") {
                canEditBoard[i][j] = false;
            } else {
                canEditBoard[i][j] = true;
            }

            currentCell++;
        }
    }

    if(solvePuzzle(board)) {
        arrayToTable();
    } else {
        openPopup();
    }
    
}

//Creates a solution for the puzzle using a brute force algorithm
function solvePuzzle(board) {
    console.log(board)
    console.log(canEditBoard)
    
    for (let row = 0; row < board.length; row++) {
        for (let col = 0; col < board.length; col++) {
          if (board[row][col] === "") {
            for (let num = 1; num <= 9; num++) {
              if (checkHorizontal(board, row, num) && checkVertical(board, col, num) && checkSquare(board, row, col, num)) {
                board[row][col] = num;
                if (solvePuzzle(board)) {
                  return true;
                }
                board[row][col] = "";
              }
            }
            return false;
          }
        }
      }
      return true;
    
}

//Reverts all data from two-dimensional array back to table
function arrayToTable() {
    cellsIndex = 0;
    for(let i = 0; i < board.length; i++) {
        for(let j = 0; j < board.length; j++) {
            cells[cellsIndex].innerHTML = board[i][j];
            cellsIndex++;
        }
    }
}

//Puzzle grid gets wiped for a new puzzle to be solved
function wipeGrid() {
    for(let i = 0; i < cells.length; i++) {
        cells[i].innerHTML = "";
    }
}

//Check if number repeats in row
function checkHorizontal(grid, i, num) {
    for(let j = 0; j < grid.length; j++) {
        if(grid[i][j] == num) {
            return false;
        }
    }

    return true;
}

//Check if number repeats in column
function checkVertical(grid, j, num) {
    for(let i = 0; i < grid.length; i++) {
        if(grid[i][j] == num) {
            return false;
        }
    }

    return true;
}

//Check if number repeats in corresponding square
function checkSquare(grid, i, j, num) {
    let row = Math.floor(i/3) * 3;
    let column = Math.floor(j/3) * 3;

    for(let m = row; m < row + 3; m++) {
        for(let n = column; n < column + 3; n++) {
            if(grid[m][n] == num) {
                return false;
            }
        }
    }

    return true;
}

function openPopup() {
    popup.classList.add("open-popup");
}

function closePopup() {
    popup.classList.remove("open-popup");
}