# Fingerprint Access Control API

**🚀 UPDATED & OPTIMIZED VERSION**

## Latest Improvements

- ✅ **True Single-Scan Verification**: Capture fingerprint ONCE and automatically identify among ALL users
- ✅ **Accurate Fingerprint Count**: `fingerprints_count` field now accurately reflects enrolled fingerprints
- ✅ **Real-time Updates**: Fingerprint counts update automatically on enrollment/deletion
- ✅ **Smart Identification**: Intelligent fallback system for optimal performance
- ✅ **No Multiple Scans**: Never asks for fingerprint more than once during identification

## Base URL

```
http://localhost:5000
```

## Health Check

### GET /api/health

Check if the API is running.

**Response:**

```json
{
  "status": "healthy",
  "message": "Fingerprint Access Control API is running"
}
```

## User Management

### POST /api/users

Create a new user.

**Request Body:**

```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response (201):**

```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "username": "john_doe"
  }
}
```

### GET /api/users

List all users with **ACCURATE** fingerprint count.

**Response:**

```json
{
  "users": [
    {
      "id": 1,
      "username": "john_doe",
      "fingerprints_count": 2
    }
  ],
  "total": 1
}
```

_Note: `fingerprints_count` now accurately reflects the number of enrolled fingerprints per user and updates automatically when fingerprints are added or removed._

### GET /api/users/{username}

Get specific user information with **ACCURATE** fingerprint count.

**Response:**

```json
{
  "id": 1,
  "username": "john_doe",
  "fingerprints_count": 2
}
```

### DELETE /api/users/{username}

Delete a user.

**Response:**

```json
{
  "message": "User john_doe deleted successfully"
}
```

### POST /api/users/{username}/verify

Verify fingerprint for specific user.

**Request Body (optional):**

```json
{
  "finger": "right-index-finger"
}
```

**Response (200 - Success):**

```json
{
  "message": "Fingerprint verification successful for user john_doe",
  "verified": true,
  "user": {
    "id": 1,
    "username": "john_doe"
  }
}
```

**Response (401 - Failed):**

```json
{
  "message": "Fingerprint verification failed",
  "verified": false
}
```

## Fingerprint Enrollment

### POST /api/enrollment/{username}

Enroll a fingerprint for an existing user.

**Request Body:**

```json
{
  "finger": "right-index-finger",
  "label": "Primary finger"
}
```

**Response:**

```json
{
  "message": "Fingerprint enrolled successfully for user john_doe",
  "user": {
    "id": 1,
    "username": "john_doe"
  },
  "fingerprint": {
    "finger": "right-index-finger",
    "label": "Primary finger"
  }
}
```

### POST /api/enrollment/user

Create a new user and enroll their first fingerprint.

**Request Body:**

```json
{
  "username": "jane_doe",
  "password": "secure_password",
  "finger": "right-index-finger",
  "label": "Primary finger"
}
```

### GET /api/enrollment/{username}/fingers

Get list of enrolled fingers for a user.

**Response:**

```json
{
  "user": {
    "id": 1,
    "username": "john_doe"
  },
  "enrolled_fingers": ["right-index-finger", "left-thumb"],
  "count": 2
}
```

### DELETE /api/enrollment/{username}/{finger}

Delete a specific fingerprint for a user.

**Response:**

```json
{
  "message": "Fingerprint right-index-finger deleted successfully for user john_doe",
  "user": {
    "id": 1,
    "username": "john_doe"
  },
  "deleted_finger": "right-index-finger"
}
```

### DELETE /api/enrollment/{username}/all

Delete all fingerprints for a user.

**Response:**

```json
{
  "message": "All fingerprints deleted successfully for user john_doe",
  "user": {
    "id": 1,
    "username": "john_doe"
  }
}
```

### GET /api/enrollment/system/status

Get comprehensive fingerprint enrollment status for the entire system.

**Response:**

```json
{
  "total_users": 3,
  "users_with_fingerprints": 2,
  "total_enrolled_fingerprints": 4,
  "users": [
    {
      "id": 1,
      "username": "john_doe",
      "enrolled_fingers": [
        {
          "finger": "right-index-finger",
          "label": "Primary Work Finger"
        },
        {
          "finger": "left-thumb",
          "label": "Backup"
        }
      ],
      "fingerprints_count": 2
    },
    {
      "id": 2,
      "username": "jane_doe",
      "enrolled_fingers": [
        {
          "finger": "right-index-finger",
          "label": "Personal"
        }
      ],
      "fingerprints_count": 1
    },
    {
      "id": 3,
      "username": "bob_smith",
      "enrolled_fingers": [],
      "fingerprints_count": 0
    }
  ],
  "system_summary": {
    "enrollment_percentage": 66.67,
    "average_fingerprints_per_user": 2.0,
    "most_used_fingers": [
      ["right-index-finger", 2],
      ["left-thumb", 1]
    ],
    "finger_distribution": {
      "right-index-finger": 2,
      "left-thumb": 1
    }
  }
}
```

### GET /api/enrollment/search/{finger}

Search for users who have enrolled a specific finger.

**Parameters:**
- `finger` (path): Finger name (e.g., "right-thumb", "left-index-finger")

**Example Request:**

```
GET /api/enrollment/search/right-thumb
```

**Response:**

```json
{
  "finger": "right-thumb",
  "users_with_finger": [
    {
      "username": "john_doe",
      "user_id": 1,
      "label": "Primary thumb for office access"
    },
    {
      "username": "alice_smith",
      "user_id": 2,
      "label": "Main identification finger"
    }
  ],
  "total_users": 2,
  "search_stats": {
    "finger_popularity_rank": 1,
    "percentage_of_users": 100.0,
    "other_popular_fingers": ["right-index-finger", "left-thumb"]
  }
}
```

### GET /api/enrollment/analytics

Get advanced system analytics including usage patterns, security insights, and recommendations.

**Response:**

```json
{
  "system_overview": {
    "total_users": 2,
    "total_fingerprints": 4,
    "enrollment_rate": 20.0,
    "average_fingers_per_user": 2.0
  },
  "finger_analytics": {
    "most_popular_fingers": [
      {
        "finger": "right-thumb",
        "count": 2,
        "percentage": 50.0
      },
      {
        "finger": "right-index-finger",
        "count": 2,
        "percentage": 50.0
      }
    ],
    "least_used_fingers": [
      "right-middle-finger",
      "right-ring-finger",
      "right-little-finger"
    ],
    "finger_distribution": {
      "right_hand": 4,
      "left_hand": 0,
      "thumb_usage": 2,
      "index_usage": 2
    }
  },
  "user_patterns": {
    "enrollment_distribution": {
      "0_fingers": 0,
      "1_finger": 0,
      "2_fingers": 2,
      "3_plus_fingers": 0
    },
    "common_finger_combinations": [
      ["right-thumb", "right-index-finger"]
    ],
    "users_with_high_security": 0,
    "users_needing_more_enrollment": 2
  },
  "security_insights": {
    "single_point_of_failure_users": 0,
    "well_protected_users": 2,
    "recommended_additional_enrollments": [
      {
        "username": "john_doe",
        "current_count": 2,
        "recommended_fingers": ["left-thumb", "left-index-finger"]
      }
    ],
    "security_score": 65.0,
    "risk_assessment": "MEDIUM"
  },
  "recommendations": [
    "Consider enrolling left-hand fingers for better redundancy",
    "Encourage users to enroll at least 3 fingers for improved security",
    "Balance finger usage across both hands",
    "Current security level is MEDIUM - consider additional enrollments"
  ],
  "label_usage": {
    "total_labeled_fingerprints": 4,
    "labeling_rate": 100.0,
    "common_label_themes": ["office", "access", "identification", "primary"]
  }
}
```

## Fingerprint Verification

### POST /api/verification

**🚀 PERFECTED:** True single-scan fingerprint identification.

**Features:**

- ✅ **Captures fingerprint only ONCE** - Never asks for multiple scans
- ✅ **Automatically processes against ALL users** - Compares with entire database
- ✅ **Smart identification algorithm** - Uses native identification when available
- ✅ **No parameters needed** - Just place finger and get identified
- ✅ **Intelligent fallback** - Optimized performance in all environments

**How it works:**

1. 📱 Single fingerprint capture
2. 📊 Automatic comparison against all enrolled users
3. ✅ Instant identification result

**Request Body:**

```json
{}
```

_Note: Empty body - no parameters needed!_

**Response (200 - Success):**

```json
{
  "message": "Fingerprint verification successful for user john_doe",
  "verified": true,
  "user": {
    "id": 1,
    "username": "john_doe"
  },
  "access_granted": true
}
```

**Response (401 - No Match):**

```json
{
  "message": "Fingerprint verification failed - no matching user found",
  "verified": false,
  "access_granted": false
}
```

### POST /api/verification/{username}

Verify fingerprint for a specific user.

**Request Body (optional):**

```json
{
  "finger": "right-index-finger"
}
```

### POST /api/verification/simulate

Simulate fingerprint verification (for testing).

**Request Body:**

```json
{
  "username": "john_doe",
  "success": true
}
```

## Error Responses

### 400 Bad Request

```json
{
  "error": "No JSON data provided"
}
```

### 404 Not Found

```json
{
  "error": "User not found"
}
```

### 409 Conflict

```json
{
  "error": "Username already exists"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error: [error details]"
}
```

## Available Fingers

- right-thumb
- right-index-finger
- right-middle-finger
- right-ring-finger
- right-little-finger
- left-thumb
- left-index-finger
- left-middle-finger
- left-ring-finger
- left-little-finger
