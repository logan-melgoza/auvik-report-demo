import { Link } from "react-router-dom";
import './NavBar.css'


function LoginButton() {

  return (
    <Link className='btn btn-primary navbar-link' to="/login">
      Login
    </Link>
  );
}

export default LoginButton;