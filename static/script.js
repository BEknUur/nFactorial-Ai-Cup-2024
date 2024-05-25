document.addEventListener('DOMContentLoaded', function () {
    var generateForm = document.getElementById('generateForm');
    var pdfButton = document.getElementById('generatePDF');
    var toggleAnswersButton = document.getElementById('toggleAnswers');

    generateForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent the default form submission
        
        var section = document.getElementById('sections').value;
        var difficulty = document.getElementById('difficulty').value;
       
        fetch('http://127.0.0.1:5000/generate-sat-problem', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ section: section, difficulty: difficulty })
        })
        .then(response => response.json())
        .then(data => {
            var outputDiv = document.getElementById('questions-output');
            outputDiv.innerHTML = '<h2>Generated Questions:</h2>';
            
            if (section === 'verbal' && data.passage) {
                outputDiv.innerHTML += `<p><strong>Passage:</strong> ${data.passage}</p>`;
                data.questions.forEach((questionObj, index) => {
                    outputDiv.innerHTML += `<p><strong>Question ${index + 1}:</strong> ${questionObj.question}</p>`;
                    outputDiv.innerHTML += '<ul>';
                    questionObj.choices.forEach((choice, idx) => {
                        outputDiv.innerHTML += `<li>${choice}</li>`;
                    });
                    outputDiv.innerHTML += '</ul>';
                    outputDiv.innerHTML += `<p class="answer"><strong>Answer:</strong> ${questionObj.answer}</p>`;
                });
            } else if (Array.isArray(data)) {
                data.forEach((questionObj, index) => {
                    outputDiv.innerHTML += `<p><strong>Question ${index + 1}:</strong> ${questionObj.question}</p>`;
                    outputDiv.innerHTML += '<ul>';
                    questionObj.choices.forEach((choice, idx) => {
                        outputDiv.innerHTML += `<li>${choice}</li>`;
                    });
                    outputDiv.innerHTML += '</ul>';
                    outputDiv.innerHTML += `<p class="answer"><strong>Answer:</strong> ${questionObj.answer}</p>`;
                });
            } else {
                outputDiv.innerHTML = '<p>No questions generated.</p>';
            }
        })
        .catch(error => console.error('Error:', error));
    });

    pdfButton.addEventListener('click', function () {
        var section = document.getElementById('sections').value;
        var difficulty = document.getElementById('difficulty').value;
       
        fetch('http://127.0.0.1:5000/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ section: section, difficulty: difficulty })
        })
        .then(response => response.blob())
        .then(blob => {
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = "sat_problems.pdf";
            document.body.appendChild(a); 
            a.click();    
            a.remove();  
        })
        .catch(error => console.error('Error:', error));
    });

    toggleAnswersButton.addEventListener('click', function () {
        var answers = document.querySelectorAll('.answer');
        answers.forEach(answer => {
            if (answer.style.display === 'none' || answer.style.display === '') {
                answer.style.display = 'block';
            } else {
                answer.style.display = 'none';
            }
        });
    });
});



