import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { login } from "../services/authService";
import './Forms.css';

function Login() {
  const { setUser } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");  
  const [password, setPassword] = useState("");  
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try{
      const { ok, status, data } = await login({ email, password });

      if (!ok) {
        return setError(data.error)
      }
      setUser(data);
      navigate("/");
    } catch {
      setError("Network error")
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 border rounded shadow-sm bg-white register-form">
      <h2 className="mb-4 form-title">Login</h2>

      <div className="mb-3 text-start">
        <label htmlFor="email" className="form-label form-label_custom">Email</label>
        <input
          type="email"
          id="email"
          className="form-control"
          placeholder="Enter email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div className="mb-3 text-start">
        <label htmlFor="password" className="form-label">Password</label>
        <input
          type="password"
          id="password"
          className="form-control"
          placeholder="Enter password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      { error ? (
        <>
          <div className="mb-3">
            <small className="auth-error">{error}</small>
          </div>
        </>
        ) : <></>
      }
      <button type="submit" className="btn btn-primary w-100 form-button" disabled={submitting}>
        {submitting ? "Logging in..." : "Login"}
      </button>
    </form>
  );
}

export default Login;