
const PropertyDetails = ({ property }) => {
    if (!property) return null;

    const fetchDocument = (docId) => {
        window.open(`http://127.0.0.1:8000/document/${docId}`, "_blank");
    };

    return (
        <div className="mt-4 p-3 border rounded shadow-sm bg-light">
            <h5 className="text-secondary">🏠 Property Details</h5>
            <p><strong>📍 Address:</strong> {property.property.address}</p>
            <p><strong>💰 Purchase Price:</strong> £{property.property.purchase_price}</p>
            <p><strong>🔹 Status:</strong> {property.property.status}</p>

            <h5 className="mt-3">📂 Documents</h5>
            {Object.entries(property.documents).length === 0 ? (
                <p>No documents available.</p>
            ) : (
                <ul className="list-group">
                    {Object.entries(property.documents).map(([category, docs]) => (
                        <li key={category} className="list-group-item">
                            <strong>{category.replace("_", " ")}:</strong>
                            {docs.map(doc => (
                                <button
                                    key={doc.id}
                                    className="btn btn-link"
                                    onClick={() => fetchDocument(doc.id)}
                                >
                                    {doc.document_type}
                                </button>
                            ))}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default PropertyDetails;



