document.addEventListener('DOMContentLoaded', function() {
    // Получаем все элементы вопросов в FAQ
    var faqQuestions = document.querySelectorAll('.faq-section dt');

    // Добавляем обработчик событий клика к каждому вопросу
    faqQuestions.forEach(function(question) {
        question.addEventListener('click', function() {
            // Переключаем класс 'active', который управляет отображением ответа
            this.classList.toggle('active');
            // Получаем следующий элемент в DOM, который должен быть ответом
            var answer = this.nextElementSibling;
            // Переключаем отображение ответа
            if (answer.style.display === 'block') {
                answer.style.display = 'none';
            } else {
                answer.style.display = 'block';
            }
        });
    });
});