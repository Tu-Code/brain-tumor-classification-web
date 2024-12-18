const baseURL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
  ? "http://127.0.0.1:8000/"  // Local development
  : "https://brain-tumor-classification-web-1.onrender.com/";  // Production development

// Function for login
async function login(username, password) {
    try {
        const response = await axios.post(`${baseURL}login`, { username, password }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
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
        const response = await axios.get(`${baseURL}results`, {
            withCredentials: true
        });
        return response.data;
    } catch (error) {
        console.error('Error getting results:', error);
        throw error;
    }
}

// Function to register results
async function registerResults(patientData) {
    try {
        const response = await axios.post(`${baseURL}results`, patientData, {
            withCredentials: true
        });
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
            withCredentials: true
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
        const response = await axios.delete(`${baseURL}patients/${email}`, {
            withCredentials: true
        });

        if (response.status === 200) {
            alert('Patient deleted successfully');
            window.location.reload();
        }
    } catch (error) {
        console.error('Error deleting patient:', error);
        alert('Error deleting patient');
    }
}