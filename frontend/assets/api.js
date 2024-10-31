const baseURL = "http://127.0.0.1:8000/"

// Function for login
async function login(username, password) {
    try {
        const response = await axios.post(`${baseURL}login`, { username, password }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        console.log(response)
        return response.data;
    } catch (error) {
        console.error('Error during login:', error);
        throw error;
    }
}
// Function for signup
async function signup(name, email, password) {
    try {
        const response = await axios.post(`${baseURL}signup`, { name, email, password });
        return response.data;
    } catch (error) {
        console.error('Error during signup:', error);
        throw error;
    }
}

// Function to get results
async function getResults() {
    try {
        const response = await axios.get(`${baseURL}results`);
        return response.data;
    } catch (error) {
        console.error('Error getting results:', error);
        throw error;
    }
}

// Function to register results
async function registerResults(patientData) {
    try {
        const response = await axios.post(`${baseURL}results`, patientData);
        return response.data;
    } catch (error) {
        console.error('Error registering results:', error);
        throw error;
    }
}

// Function to predict tumor subtype
async function predict(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post(`${baseURL}predict`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Error during prediction:', error);
        throw error;
    }
}

// Function to delete a patient
async function deletePatient(email) {
    try {
        const response = await axios.delete(`${baseURL}patients/${email}`);
        if (response.status === 200) {
            alert('Patient deleted successfully');
            window.location.reload();
        }
    } catch (error) {
        console.error('Error deleting patient:', error);
        alert('Error deleting patient');
    }
}