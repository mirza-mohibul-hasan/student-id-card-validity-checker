import { useState } from "react";
import axios from "axios";
import ClockLoader from "react-spinners/ClockLoader";
const UploadForm = () => {
  const [name, setName] = useState("");
  const [university, setUniversity] = useState("");
  const [image, setImage] = useState(null);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [model, setModel] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResponse(null);
    if (!name || !university || !image) {
      setError("Please fill out all fields.");
      return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("university", university);
    formData.append("image", image);

    try {
      setIsLoading(true);
      const res = await axios.post(
        model === 1
          ? "http://localhost:5000/process-image-yolo"
          : "http://localhost:5000/process-image-nlp",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      setResponse(res.data);
      setError(null);
    } catch (err) {
      setError("Error uploading data.");
      console.log(err);
      setResponse(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-4 p-6 bg-white rounded-lg shadow-md">
      <p className="text-md py-2 text-center">
        Please Choose a Model, Default is YOLO
      </p>
      <div className="flex w-full">
        <button
          onClick={() => setModel(1)}
          className={`card rounded-box grid h-10 flex-grow place-items-center ${
            model === 1 ? "bg-blue-500 text-white" : "bg-base-200"
          }`}
        >
          YOLO Model
        </button>
        <div className="divider divider-horizontal">OR</div>
        <button
          onClick={() => setModel(2)}
          className={`card rounded-box grid h-10 flex-grow place-items-center ${
            model === 2 ? "bg-blue-500 text-white" : "bg-base-200"
          }`}
        >
          NLP Model
        </button>
      </div>
      <h1 className="text-2xl font-bold mb-4 text-center">
        ID Card Validation
      </h1>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 font-bold mb-2" htmlFor="name">
            Name:
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your name"
          />
        </div>

        <div className="mb-4">
          <label
            className="block text-gray-700 font-bold mb-2"
            htmlFor="university"
          >
            University:
          </label>
          <input
            type="text"
            id="university"
            value={university}
            onChange={(e) => setUniversity(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter university name"
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 font-bold mb-2" htmlFor="image">
            Upload ID Card:
          </label>
          <input
            type="file"
            id="image"
            onChange={handleImageChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-500 text-white font-bold py-2 px-4 rounded-md hover:bg-blue-600"
        >
          Submit
        </button>

        {error && <p className="text-red-500 mt-4">{error}</p>}
      </form>

      {isLoading && (
        <div className="flex flex-col items-center my-4">
          <p className="text-center">Loading..... Please Wait🙂</p>
          <div>
            <ClockLoader />
          </div>
        </div>
      )}

      {response && (
        <div className="mt-4 p-4 bg-gray-100 rounded-md">
          <h2 className="text-lg font-bold text-center border-b-2">
            Validation Results
          </h2>
          <p>
            <strong>ID Card Valid:</strong>{" "}
            {response.is_valid_card ? "Yes" : "No"}
          </p>
          <p>
            <strong>Name Match:</strong> {response.name_match}%
          </p>
          <p>
            <strong>University Match:</strong> {response.university_match}%
          </p>
          <p>
            <strong>Expiration Status:</strong>{" "}
            {response.is_expired ? "Expired" : "Valid"}
          </p>

          <div className="mt-4">
            <h3 className="text-lg font-bold text-center border-b-2">
              Test Results
            </h3>
            <p>
              <strong>Detected Name:</strong> {response.fields.Name}
            </p>
            <p>
              <strong>Detected University:</strong> {response.fields.University}
            </p>
            <p>
              <strong>Detected Expiration:</strong> {response.fields.Expiration}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadForm;
