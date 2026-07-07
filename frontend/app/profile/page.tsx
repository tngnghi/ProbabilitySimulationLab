import ProtectedRoute from '@/components/ProtectedRoute';

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <div>
        <h1>Profile</h1>
        <p>User profile page coming soon.</p>
      </div>
    </ProtectedRoute>
  );
}