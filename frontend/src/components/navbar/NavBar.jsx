import { useAuth } from '../../context/AuthContext';
import LoginButton from './LoginButton'
import RegisterButton from './RegisterButton'
import LogoutButton from './LogoutButton';
import './NavBar.css'

function NavBar() {
  const { user } = useAuth()

  return (
    <>
      {user ? (
        <div className='navbar'>
          <div className='navbar-buttons' style={{ visibility: "hidden" }}>
            <LogoutButton />
          </div>
          <div className='navbar-title'>
            <h1>Auvik Network Reports</h1>
          </div>
          <div className='navbar-buttons'>
            <LogoutButton />
          </div>
        </div>
      ) : (
        <div className='navbar'>
          <div className='navbar-buttons' style={{ visibility: "hidden" }}>
            <RegisterButton />
            <LoginButton />
          </div>
          <div className='navbar-title'>
            <h1>Auvik Network Reports</h1>
          </div>
          <div className='navbar-buttons'>
            <RegisterButton />
            <LoginButton />
          </div>
        </div>
      )}
    </>
  );
}

export default NavBar;