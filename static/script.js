const canvas = document.getElementById('canvas')
const ctx = canvas.getContext('2d')
let drawing = false
const historyContainer = document.getElementById('history')
let captureInterval
let currentWord = ''
let lastDrawnPoint = { x: 0, y: 0 }
let erasing = false
const colorPicker = document.getElementById('color_picker')
let currentColor = colorPicker.value

colorPicker.addEventListener('change', event => {
    currentColor = event.target.value
})

document.getElementById('clear').addEventListener('click', clearCanvas)
document.getElementById('eraser').addEventListener('click', () => {
    erasing = !erasing
    const eraserButton = document.getElementById('eraser')
    if (erasing) {
        ctx.strokeStyle = 'white'
        eraserButton.classList.add('erasing-active')
        console.log(a)
    } else {
        ctx.strokeStyle = currentColor
        eraserButton.classList.remove('erasing-active')
    }
})

document.getElementById('generate_word_button').addEventListener('click', () => {
    generateWord()
    clearCanvasAndHistory()
})

function draw(event) {
    if (!drawing) return
    ctx.lineWidth = 5
    ctx.lineCap = 'round'

    if (!erasing) {
        ctx.strokeStyle = currentColor
    }

    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    ctx.lineTo(x, y)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(x, y)

    lastDrawnPoint = { x, y }
}

function generateWord() {
    fetch('/generate_word')
    .then(response => response.json())
    .then(data => {
        const word = data.word
        currentWord = word
        document.getElementById('word_to_draw').textContent = word

        if (captureInterval) {
            clearInterval(captureInterval)
        }

         captureInterval = setInterval(captureAndSend, 15000)
    })
}

function captureAndSend() {
    const dataURL = canvas.toDataURL('image/png')
    const guessedWord = currentWord

    fetch('/check_drawing', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: dataURL, guessed_word: guessedWord })
     })
    .then(response => response.json())
    .then(data => {
        const { prediction, correct } = data
        updateHistory(prediction, correct)
        if (correct) {
            clearInterval(captureInterval)
            showSuccessModal()
        }
    })
}

function showSuccessModal() {
    const modal = document.getElementById('successModal')
    modal.style.display = 'block'

    lastDrawnPoint = { x: 0, y: 0 }
}

function updateHistory(prediction, correct) {
    const p = document.createElement('p')
    p.textContent = `Gemini: ${prediction}`
    p.classList.add(correct ? 'correct' : 'incorrect')
    historyContainer.appendChild(p)
    historyContainer.scrollTop = historyContainer.scrollHeight
}

function updateCanvasSize() {
    const canvasContainer = document.querySelector('.canvas')
    canvas.width = canvasContainer.offsetWidth
    canvas.height = canvasContainer.offsetHeight

    ctx.fillStyle = 'white'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
}

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.beginPath()

    ctx.fillStyle = 'white'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
}

function clearCanvasAndHistory() {
    clearCanvas()
    historyContainer.innerHTML = ''
}

window.addEventListener('load', () => {
    updateCanvasSize()
    canvas.addEventListener('mousedown', event => {
        drawing = true
        const rect = canvas.getBoundingClientRect()
        const x = event.clientX - rect.left
        const y = event.clientY - rect.top
        ctx.moveTo(x, y)
    })
    document.addEventListener('mouseup', () => {
        if (drawing) {
        drawing = false
        ctx.beginPath()
        }
    })
    canvas.addEventListener('mousemove', draw)
})

const playAgainButton = document.getElementById('playAgain')
const stopButton = document.getElementById('stop')

playAgainButton.addEventListener('click', () => {
    closeModal()
    generateWord()
    clearCanvasAndHistory()
})

stopButton.addEventListener('click', () => {
    closeModal()
    clearInterval(captureInterval)
})

function closeModal() {
    const modal = document.getElementById('successModal')
    modal.style.display = 'none'
}