import { useState } from "react";

const PropertyDetails = () => {
    const [propertyId, setPropertyId] = useState("");
    const [address, setAddress] = useState("");
    const [price, setPrice] = useState("");
    const [status, setStatus] = useState("");

    // const handleSubmit = async (e) => {
    //     e.preventDefault();

    //     const response = await fetch("http://127.0.0.1:8000/upload_property_details", {
    //         method: "POST",
    //         body: formData,
            
    //         // body: JSON.stringify({
    //         //     propertyId,
    //         //     address,
    //         //     purchase_price: parseFloat(price),
    //         //     status
    //         // })
    //     });

    //     const result = await response.json();

    //     if (response.ok) {
    //         alert(`Property added with ID: ${result.property_id}`);
    //     } else {
    //         alert(`Failed to add property: ${result.detail}`);
    //     }

 

    // };

    const handleSubmit = async (e) => {
        e.preventDefault();
    
        const formData = new FormData();
        formData.append("property_id", propertyId);
        formData.append("address", address);
        formData.append("purchase_price", price);
        formData.append("status", status);
    
        const response = await fetch("http://127.0.0.1:8000/upload_property_details", {
            method: "POST",
            body: formData,
        });
    
        const result = await response.json();
    
        if (response.ok) {
            alert(`Property added with ID: ${result.property_id}`);
        } else {
            alert(`Failed to add property: ${result.detail}`);
        }
    };
    

    return (
        <div className="card p-4 my-4">
            <h4>Add New Property</h4>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label className="form-label">Property ID:</label>
                    <input
                        type="number"
                        className="form-control"
                        value={propertyId}
                        onChange={(e) => setPropertyId(e.target.value)}
                        required
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Address</label>
                    <input className="form-control" value={address} onChange={(e) => setAddress(e.target.value)} required />
                </div>
                <div className="mb-3">
                    <label className="form-label">Purchase Price (£)</label>
                    <input className="form-control" type="number" value={price} onChange={(e) => setPrice(e.target.value)} required />
                </div>
                <div className="mb-3">
                    <label className="form-label">Status</label>
                    <select className="form-select" value={status} onChange={(e) => setStatus(e.target.value)} required>
                        <option value="">Select status</option>
                        <option value="purchased">Purchased</option>
                        <option value="renovating">Renovating</option>
                        <option value="for sale">For Sale</option>
                        <option value="sold">Sold</option>
                    </select>
                </div>
                <button type="submit" className="btn btn-success">Add Property</button>
            </form>
        </div>
    );
};

export default PropertyDetails;