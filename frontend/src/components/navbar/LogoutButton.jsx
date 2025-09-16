import { useState } from "react";
import { useAuth } from "../../context/AuthContext"
import { logout } from "../../services/authService";
import './NavBar.css'

function LogoutButton() {
  const { setUser } = useAuth();
  const [loading, setLoading] = useState(false);

  async function handleLogout() {
    try {
      setLoading(true);
      await logout();
      setUser(null);
      console.log("Successful logout");
      window.location.reload();
    } catch (e) {
      console.error("Logout failed", e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <button className='btn btn-primary navbar-button' onClick={handleLogout}>
      {loading ? "Logging Out" : "Logout"}
    </button>
  );
}
export default LogoutButton;