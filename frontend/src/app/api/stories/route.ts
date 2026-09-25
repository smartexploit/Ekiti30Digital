import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { fullName, email, title, category, content } = body;

    if (!fullName || !email || !title || !content) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Log received story payload
    console.log('New story submission:', {
      fullName,
      email,
      title,
      category,
      content,
      submittedAt: new Date().toISOString(),
    });

    return NextResponse.json(
      { message: 'Story submitted successfully' },
      { status: 201 }
    );
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error processing story submission' },
      { status: 500 }
    );
  }
}
