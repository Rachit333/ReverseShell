import React, { useState } from 'react';
import axios from 'axios';

function Signup() {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: ''
    });

    const { username, email, password } = formData;

    const onChange = e => setFormData({ ...formData, [e.target.name]: e.target.value });

    const onSubmit = async e => {
        e.preventDefault();
        try {
            const res = await axios.post('http://localhost:5000/api/auth/signup', formData);
            localStorage.setItem('token', res.data.token);
            alert('Signup successful');
        } catch (err) {
            console.error(err);
            alert('Signup failed');
        }
    };

    return (
        <div>
            <h2>Signup</h2>
            <form onSubmit={onSubmit}>
                <input 
                    type="text" 
                    name="username" 
                    value={username} 
                    onChange={onChange} 
                    placeholder="Username" 
                    required 
                />
                <input 
                    type="email" 
                    name="email" 
                    value={email} 
                    onChange={onChange} 
                    placeholder="Email" 
                    required 
                />
                <input 
                    type="password" 
                    name="password" 
                    value={password} 
                    onChange={onChange} 
                    placeholder="Password" 
                    required 
                />
                <button type="submit">Signup</button>
            </form>
        </div>
    );
}

export default Signup;
