document.addEventListener('DOMContentLoaded', function () {
    var projectSelect = document.getElementById('project');
    var serverSelect = document.getElementById('server');

    var serversByProject = {
        'GTA5RP': [
            'Downtown', 'Strawberry', 'Vinewood', 'Blackberry', 'Insquad', 'Sunrise', 'Rainbow', 'Richman', 'Eclipse', 'La Mesa', 'Burton', 'Rockford', 'Alta', 'Del Perro', 'Davis', 'Harmony', 'Redwood', 'Hawick', 'Grapeseed'
        ],
        'Madjestic': [
            'New York', 'Detroit', 'Chicago', 'San Francisco', 'Atlanta', 'San Diego', 'Los Angeles', 'Miami', 'Las Vegas', 'Washington'
        ]
    };

    projectSelect.addEventListener('change', function () {
        var selectedProject = this.value;
        var servers = serversByProject[selectedProject] || [];
        serverSelect.innerHTML = ''; // Очищаем список серверов
        serverSelect.disabled = !servers.length; // Делаем селект активным/неактивным

        servers.forEach(function (server) {
            var option = document.createElement('option');
            option.value = server;
            option.textContent = server;
            serverSelect.appendChild(option);
        });

        // Если используется Select2, обновляем его состояние
        $(serverSelect).select2({
            placeholder: 'Выберите сервер',
            allowClear: true
        }).trigger('change');
    });

    // Инициализация Select2 для поля выбора сервера
    $(serverSelect).select2({
        placeholder: 'Выберите сервер',
        allowClear: true
    });


    // Скрытие GIF анимации загрузки
    document.getElementById('loadingGifContainer').style.display = 'none';
});