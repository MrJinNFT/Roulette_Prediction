document.addEventListener('DOMContentLoaded', function () {
    const numberToColor = {
        "1": "red", "3": "red", "5": "red", "7": "red", "9": "red",
        "12": "red", "14": "red", "16": "red", "18": "red", "19": "red",
        "21": "red", "23": "red", "25": "red", "27": "red", "30": "red",
        "32": "red", "34": "red", "36": "red",
        "2": "black", "4": "black", "6": "black", "8": "black", "10": "black",
        "11": "black", "13": "black", "15": "black", "17": "black", "20": "black",
        "22": "black", "24": "black", "26": "black", "28": "black", "29": "black",
        "31": "black", "33": "black", "35": "black",
        "0": "green", "00": "green"
    };

    const rouletteNumbers = document.querySelectorAll('.roulette-number');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorElement = document.getElementById('error');
    const predictionElement = document.getElementById('predictions');
    const guessedHistoryElement = document.getElementById('guessed-history ul'); // Element for guessed history
    const aiDisclaimer = document.createElement('div');
    aiDisclaimer.innerHTML = "<p class='ai-disclaimer'>Внимание: Не полагайтесь на предсказания AI на данном этапе. Модель все еще обучается (Не ставьте ставки полагаясь на предсказания. ждите обновления.).</p>";
    
    predictionElement.before(aiDisclaimer);

    rouletteNumbers.forEach(function (numberElement) {
        numberElement.addEventListener('click', function () {
            let selectedNumber = numberElement.getAttribute('data-number');
            console.log(selectedNumber);
            loadingIndicator.style.display = 'block';
            errorElement.style.display = 'none';

            const username = localStorage.getItem('username');
            const tableNumber = localStorage.getItem('tableNumber');

            fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `number=${encodeURIComponent(selectedNumber)}&username=${encodeURIComponent(username)}&tableNumber=${encodeURIComponent(tableNumber)}&server=${encodeURIComponent(document.getElementById('hiddenServerField').value)}`
            })
            .then(response => {
                loadingIndicator.style.display = 'none';
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                predictionElement.innerHTML = ''; 
                const predictionRows = [[], []]; 

                data.predictions.forEach((prediction, index) => {
                    const numberDisplay = prediction.number === "00" ? "00" : prediction.number;
                    const colorClass = `${numberToColor[numberDisplay]}-background`;
                    const div = document.createElement('div');
                    div.classList.add('prediction-item');
                    div.innerHTML = `
                        <span class="prediction-number ${colorClass}">${numberDisplay}</span>
                        <span class="probability">${prediction.probability}</span>
                    `;
                    if (prediction.hot) {
                        const hotLabel = document.createElement('span');
                        hotLabel.classList.add('label', 'hot');
                        hotLabel.textContent = 'Hot';
                        div.appendChild(hotLabel);
                    }
                    if (prediction.new) {
                        const newLabel = document.createElement('span');
                        newLabel.classList.add('label', 'new');
                        newLabel.textContent = 'New';
                        div.appendChild(newLabel);
                    }
                    if (prediction.AI) {  
                        const aiLabel = document.createElement('span');
                        aiLabel.classList.add('label', 'ai');
                        aiLabel.textContent = 'AI';
                        div.appendChild(aiLabel);
                    }
                    if (prediction.dubl) {
                        const dublLabel = document.createElement('span');
                        dublLabel.classList.add('label', 'dubl');
                        dublLabel.textContent = 'Dubl';
                        div.appendChild(dublLabel);
                    }
                    predictionRows[Math.floor(index / 3)].push(div); 
                });

                predictionRows.forEach(row => {
                    const rowDiv = document.createElement('div');
                    rowDiv.classList.add('prediction-row');
                    row.forEach(item => rowDiv.appendChild(item));
                    predictionElement.appendChild(rowDiv);
                });

                // Update guessed history
                guessedHistoryElement.innerHTML = '';
                data.guessed_history.forEach(entry => {
                    const li = document.createElement('li');
                    li.textContent = `${entry.predictor} угадал число ${entry.number}`;
                    guessedHistoryElement.appendChild(li);
                });
            })
            .catch(error => {
                errorElement.style.display = 'block';
                errorElement.textContent = 'Спасибо: Модель приняла ваши данные. надеюсь это не всё.';
                console.error('Error:', error);
            });
        });
    });

    const numbers = document.querySelectorAll('.roulette-number');
    const selectedNumber = document.getElementById('selected-number');

    numbers.forEach(function(number) {
        number.addEventListener('click', function() {
            const selectedValue = this.getAttribute('data-number');
            selectedNumber.textContent = selectedValue;
            const color = numberToColor[selectedValue];
            selectedNumber.style.backgroundColor = color;
            numbers.forEach(function(num) {
                num.classList.remove('selected');
            });
            this.classList.add('selected');
        });
    });
});
