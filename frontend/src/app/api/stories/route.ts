import { NextResponse } from 'next/server';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const response = await fetch(`${FASTAPI_URL}/api/stories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error forwarding request to FastAPI backend:', error);
    return NextResponse.json(
      { error: 'Failed to submit story to backend service' },
      { status: 500 }
    );
  }
}
