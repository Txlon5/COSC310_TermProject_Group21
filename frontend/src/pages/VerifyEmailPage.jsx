import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { verifyEmail } from "../api";

export default function VerifyEmailPage() {
  const { tokenId } = useParams();
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    verifyEmail(tokenId)
      .then(() => setStatus("success"))
      .catch((err) => {
        setError(err.message);
        setStatus("error");
      });
  }, [tokenId]);

  return (
    <div className="auth-container">
      <div className="card auth-card">
        <h2>Email Verification</h2>
        {status === "loading" && <p>Verifying your account…</p>}
        {status === "success" && (
          <>
            <div className="alert success">Your account has been verified!</div>
            <p className="auth-footer">
              <Link to="/login">Sign in</Link>
            </p>
          </>
        )}
        {status === "error" && (
          <>
            <div className="alert error">{error}</div>
            <p className="auth-footer">
              <Link to="/login">Back to Sign In</Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
