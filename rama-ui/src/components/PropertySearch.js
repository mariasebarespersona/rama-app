// import { useState } from "react";
// console.log("PropertySearch component loaded");

// const PropertySearch = () => {
//     console.log("Property search function being executed");
//     const [propertyId, setPropertyId] = useState("");  // Store user input
//     const [propertyData, setPropertyData] = useState(null); // Store API response

//     const handleSearch = async () => {
//         console.log("Search button clicked!");
    
//         if (!propertyId) {
//             alert("Please enter a property ID!");
//             return;
//         }
    
//         try {
//             let response = await fetch(`http://127.0.0.1:8000/api/property/${propertyId}`, {
//                 method: "GET",
//                 headers: { 
//                     "Accept": "application/json",
//                     "Content-Type": "application/json"
//                 },
//             });
    
//             let textResponse = await response.text(); // Read response as text
//             console.log("Raw response:", textResponse); // Log raw response for debugging
    
//             if (!response.ok) {
//                 throw new Error(`HTTP error! Status: ${response.status}`);
//             }
    
//             let data;
//             try {
//                 data = JSON.parse(textResponse); // Convert to JSON
//             } catch (parseError) {
//                 console.error("Error parsing JSON:", parseError);
//                 alert("Invalid JSON response from server. See console for details.");
//                 return;
//             }
    
//             console.log("Parsed JSON:", data);
    
//             if (!data.property) {
//                 alert("Property not found!");
//             } else {
//                 setPropertyData(data);
//             }
//         } catch (error) {
//             console.error("Error fetching properties:", error);
//             alert("Error fetching properties. See console for details.");
//         }
//     };
    
    
 


//     return (
//         <div>
//             <h2>Search for a Property</h2>
//             <input
//                 type="text"
//                 value={propertyId}
//                 onChange={(e) => setPropertyId(e.target.value)}
//                 placeholder="Enter Property ID"
//             />
//             <button onClick={() => {
//                 console.log("Search button clicked!"); 
//                 handleSearch();
//                 }}>Search</button>


//             {propertyData && (
//                 <div>
//                     <h3>Property Details</h3>
//                     <p><strong>Address:</strong> {propertyData.address}</p>
                    
//                     <h3>Documents</h3>
//                     {propertyData.documents &&
//                         Object.entries(propertyData.documents).map(([category, docs]) => (
//                             <div key={category}>
//                                 <h4>{category.replace("_", " ")}</h4>
//                                 <ul>
//                                     {docs.map((doc, index) => (
//                                         <li key={index}>{doc.document_type}</li>
//                                     ))}
//                                 </ul>
//                             </div>
//                         ))
//                     }
//                 </div>
//             )}

//         </div>
//     );
// };

// export default PropertySearch;

import { useState } from "react";
import PropertyDetails from "./PropertyDetails";

const PropertySearch = () => {
    const [propertyId, setPropertyId] = useState("");
    const [propertyData, setPropertyData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSearch = async () => {
        if (!propertyId) {
            setError("Please enter a Property ID.");
            return;
        }

        setLoading(true);
        setError("");
        setPropertyData(null);

        try {
            let response = await fetch(`http://127.0.0.1:8000/api/property/${propertyId}`, {
                method: "GET",
                headers: { "Accept": "application/json" },
            });

            if (!response.ok) throw new Error(`Property not found!`);

            const data = await response.json();
            setPropertyData(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card p-4 shadow">
            <h4 className="text-primary">🔍 Search for a Property</h4>
            {error && <p className="alert alert-danger">{error}</p>}
            <div className="input-group mb-3">
                <input
                    type="text"
                    className="form-control"
                    placeholder="Enter Property ID"
                    value={propertyId}
                    onChange={(e) => setPropertyId(e.target.value)}
                />
                <button className="btn btn-primary" onClick={handleSearch} disabled={loading}>
                    {loading ? "Searching..." : "Search"}
                </button>
            </div>
            {propertyData && <PropertyDetails property={propertyData} />}
        </div>
    );
};

export default PropertySearch;
