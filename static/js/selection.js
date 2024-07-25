document.addEventListener('DOMContentLoaded', function () {
    var projectSelect = document.getElementById('project');
    var serverSelect = document.getElementById('server');
    var goToPredictionsButton = document.getElementById('go-to-predictions');
    var usernameInput = document.getElementById('username');
    var serversByProject = {
        'GTA5RP': [
            'Downtown', 'Strawberry', 'Vinewood', 'Blackberry', 'Insquad', 'Sunrise', 'Rainbow', 'Richman', 'Eclipse', 'La Mesa', 'Burton', 'Rockford', 'Alta', 'Del Perro', 'Davis', 'Harmony', 'Redwood', 'Hawick', 'Grapeseed'
        ],
        'Madjestic': [
            'New York', 'Detroit', 'Chicago', 'San Francisco', 'Atlanta', 'San Diego', 'Los Angeles', 'Miami', 'Las Vegas', 'Washington'
        ]
    };

    // Функция для обновления списка серверов
    function updateServerList() {
        var selectedProject = projectSelect.value;
        var servers = serversByProject[selectedProject] || [];
        serverSelect.innerHTML = ''; // Очищаем список серверов

        servers.forEach(function (server) {
            var option = document.createElement('option');
            option.value = server;
            option.textContent = server;
            serverSelect.appendChild(option);
        });

        // Обновляем Select2 для нового списка серверов
        $(serverSelect).select2({
            placeholder: 'Выберите сервер',
            allowClear: true
        }).trigger('change');

        // Загружаем сохраненное значение сервера из localStorage
        var savedServer = localStorage.getItem('server');
        if (savedServer) {
            serverSelect.value = savedServer;
            $(serverSelect).trigger('change');
        }
    }

    // Вызываем функцию updateServerList при загрузке страницы
    updateServerList();

    // Вызываем функцию updateServerList при изменении выбранного проекта
    projectSelect.addEventListener('change', updateServerList);

    // Инициализация Select2 для выпадающего списка проектов
    $(projectSelect).select2({
        placeholder: 'Выберите проект',
        allowClear: true
    });

    // Загружаем сохраненное значение проекта из localStorage
    var savedProject = localStorage.getItem('project');
    if (savedProject) {
        projectSelect.value = savedProject;
        $(projectSelect).trigger('change');
    }

    // Загружаем сохраненное значение имени пользователя из localStorage
    var savedUsername = localStorage.getItem('username');
    if (savedUsername) {
        usernameInput.value = savedUsername;
    }

    goToPredictionsButton.addEventListener('click', function () {
        var selectedServer = serverSelect.value; // Получаем выбранное имя сервера
        var username = usernameInput.value; // Получаем имя пользователя

        if (username.trim() === '') {
            alert('Пожалуйста, введите имя пользователя.');
            return;
        }

        document.getElementById('hiddenServerField').value = selectedServer; // Обновляем скрытое поле

        // Сохраняем значения в localStorage
        localStorage.setItem('username', username);
        localStorage.setItem('project', projectSelect.value);
        localStorage.setItem('server', selectedServer);

        // Переход на страницу предсказаний с именем пользователя и сервером
        window.location.href = `/predicts?server=${selectedServer}&username=${username}`;
    });
});
