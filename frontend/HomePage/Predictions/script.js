document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.querySelector('#prediction-table tbody');
    const addBtn = document.getElementById('add-btn');

    // Add student functionality
    addBtn.addEventListener('click', () => {
        const newRow = document.createElement('tr');

        const patientIdCell = document.createElement('td');
        patientIdCell.contentEditable = true;
        patientIdCell.classList.add('patient-id');
        patientIdCell.style.cursor = "pointer";

        const lastNameCell = document.createElement('td');
        lastNameCell.contentEditable = true;

        const firstNameCell = document.createElement('td');
        firstNameCell.contentEditable = true;

        const diseaseCell = document.createElement('td');
        diseaseCell.contentEditable = true;

        const predictionCell = document.createElement('td');
        predictionCell.contentEditable = true;

        newRow.appendChild(patientIdCell);
        newRow.appendChild(lastNameCell);
        newRow.appendChild(firstNameCell);
        newRow.appendChild(diseaseCell);
        newRow.appendChild(predictionCell);

        tableBody.appendChild(newRow);

        patientIdCell.addEventListener('click', () => {
            const studentId = patientIdCell.textContent.trim();
            if (patientId) {
                window.location.href = `patient-details.html?patientId=${patientId}`;
            }
        });
    });
});
