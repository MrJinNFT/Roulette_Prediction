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
    const guessedHistoryElement = document.getElementById('guessed-history').querySelector('ul');

    if (!predictionElement || !guessedHistoryElement) {
        console.error('Не удалось найти элементы predictions или guessed-history');
        return;
    }

    rouletteNumbers.forEach(function (numberElement) {
        numberElement.addEventListener('click', function () {
            let selectedNumber = numberElement.getAttribute('data-number');
            console.log(selectedNumber);
            if (loadingIndicator) loadingIndicator.style.display = 'block';
            if (errorElement) errorElement.style.display = 'none';

            const username = localStorage.getItem('username');
            const server = document.getElementById('hiddenServerField').value;

            fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'number': selectedNumber,
                    'username': username,
                    'server': server
                })
            })
            .then(response => {
                if (loadingIndicator) loadingIndicator.style.display = 'none';
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log(data); // Логирование полученных данных

                if (data.error) {
                    if (errorElement) {
                        errorElement.textContent = data.error;
                        errorElement.style.display = 'block';
                    }
                    return;
                }

                // Очистка элементов предсказаний
                predictionElement.innerHTML = '';

                // Отображение предсказаний в две строки
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
                    if (prediction.source === 'AI') {
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

                    div.addEventListener('click', function() {
                        fetch('/guessed', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded',
                            },
                            body: new URLSearchParams({
                                'number': numberDisplay,
                                'username': username,
                                'server': server
                            })
                        })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Network response was not ok');
                            }
                            return response.json();
                        })
                        .then(guessedData => {
                            guessedHistoryElement.innerHTML = '';
                            guessedData.forEach(entry => {
                                const li = document.createElement('li');
                                li.textContent = `${entry.predictor} угадал число ${entry.number}`;
                                guessedHistoryElement.appendChild(li);
                            });
                        })
                        .catch(error => {
                            console.error('There was a problem with the fetch operation:', error);
                        });
                    });

                    predictionRows[Math.floor(index / 3)].push(div); 
                });

                predictionRows.forEach(row => {
                    const rowDiv = document.createElement('div');
                    rowDiv.classList.add('prediction-row');
                    row.forEach(item => rowDiv.appendChild(item));
                    predictionElement.appendChild(rowDiv);
                });

                // Обновление истории угаданных чисел
                guessedHistoryElement.innerHTML = '';
                data.guessed_history.forEach(entry => {
                    const li = document.createElement('li');
                    li.textContent = `${entry.predictor} угадал число ${entry.number}`;
                    guessedHistoryElement.appendChild(li);
                });

                // Обновление с последним выпавшим числом
                fetch('/update_last_number', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'number': selectedNumber,
                        'username': username,
                        'server': server
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(updateData => {
                    console.log('Последнее число обновлено в базе данных:', updateData);
                })
                .catch(error => {
                    console.error('There was a problem with the update operation:', error);
                });
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                if (errorElement) {
                    errorElement.textContent = 'Произошла ошибка: ' + error.message;
                    errorElement.style.display = 'block';
                }
            });
        });
    });

    const numbers = document.querySelectorAll('.roulette-number');
    const selectedNumber = document.getElementById('selected-number');

    numbers.forEach(function(number) {
        number.addEventListener('click', function() {
            const selectedValue = this.getAttribute('data-number');
            if (selectedNumber) {
                selectedNumber.textContent = selectedValue;
                const color = numberToColor[selectedValue];
                selectedNumber.style.backgroundColor = color;
                numbers.forEach(function(num) {
                    num.classList.remove('selected');
                });
                this.classList.add('selected');
            }
        });
    });
});
