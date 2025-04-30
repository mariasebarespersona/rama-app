import { useState } from "react";

const UploadForm = () => {
    const [propertyId, setPropertyId] = useState("");
    const [docType, setDocType] = useState("");
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState("");

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!propertyId || !docType || !file) {
            setMessage("Please fill in all fields.");
            return;
        }

        setUploading(true);
        setMessage("");

        const formData = new FormData();
        formData.append("property_id", propertyId);
        formData.append("doc_type", docType);
        formData.append("file", file);

        try {
            const response = await fetch("http://127.0.0.1:8000/upload", {
                method: "POST",
                body: formData,
            });

            const result = await response.json();
            setMessage(result.message);
        } catch (error) {
            setMessage("Upload failed. Please try again.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="card p-4 shadow">
            <h4 className="text-primary">📤 Upload a Document</h4>
            {message && <p className="alert alert-info">{message}</p>}
            <form onSubmit={handleUpload}>
                <div className="mb-3">
                    <label className="form-label">Property ID:</label>
                    <input 
                        type="number" className="form-control"
                        value={propertyId} onChange={(e) => setPropertyId(e.target.value)}
                        required
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Document Type:</label>
                    <select className="form-select" value={docType} onChange={(e) => setDocType(e.target.value)}>
                        <option value="">Select a document type</option>
                        <option value="contract">Contract</option>
                        <option value="notary_deed">Notary Deed</option>
                        <option value="notary_registration">Notary Registration</option>
                        <option value="deposit">Deposit</option>
                        <option value="tax_ITP_IBA">Tax ITP IBA</option>
                        <option value="builder_payments">Builders Payments</option>
                        <option value="geotechnical_study">Geotechnical Study</option>
                        <option value="land_plans">Land Plans</option>
                        <option value="architect_plans">Architect Plans</option>
                        <option value="budget">Budget</option>
                        <option value="architect_contract">Architect Contract</option>
                        <option value="surveyor_contract">Surveyor Contract</option>
                        <option value="building_license">Building License</option>
                        <option value="contractor_contract">Contractor Contract</option>
                        <option value="trade_contract">Trade Contract</option>
                        <option value="sale_contract">Sale Contract</option>
                        <option value="payment_certification">Payment Certifications</option>

                    </select>
                </div>
                <div className="mb-3">
                    <label className="form-label">Upload File:</label>
                    <input 
                        type="file" className="form-control"
                        onChange={(e) => setFile(e.target.files[0])}
                        required
                    />
                </div>
                <button type="submit" className="btn btn-success w-100" disabled={uploading}>
                    {uploading ? "Uploading..." : "Upload"}
                </button>
            </form>
        </div>
    );
};

export default UploadForm;
