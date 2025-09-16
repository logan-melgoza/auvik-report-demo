import './TenantCard.css'
import './transitions.css'

function TenantCard({ name, selected, onClick }) {
  return (
    <div 
      className={ !selected ? 'card tenant-card' : 'card tenant-card selected'}
      style={{ width: "10rem" }}
      onClick={onClick}
    >
      <div className='card-body tenant-card-body'>
        <p className='card-text'>
          {name}
        </p>
      </div>
    </div>
  );
}

export default TenantCard;