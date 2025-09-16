import { Link } from 'react-router-dom';
import './NavBar.css';

function RegisterButton() {

    return (
        <Link className='btn btn-primary navbar-link' to='/register'>
            Register
        </Link>
    );
}

export default RegisterButton;