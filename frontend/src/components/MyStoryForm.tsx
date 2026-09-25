'use client';

import React, { useState } from 'react';

interface StoryFormData {
  fullName: string;
  email: string;
  title: string;
  category: string;
  content: string;
}

export const MyStoryForm: React.FC = () => {
  const [formData, setFormData] = useState<StoryFormData>({
    fullName: '',
    email: '',
    title: '',
    category: 'Education',
    content: '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setStatusMessage(null);

    try {
      const response = await fetch('/api/stories', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to submit your story. Please try again.');
      }

      setStatusMessage({ type: 'success', text: 'Thank you! Your story has been submitted successfully.' });
      setFormData({
        fullName: '',
        email: '',
        title: '',
        category: 'Education',
        content: '',
      });
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'An unexpected error occurred.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-md my-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">Share Your Story</h2>
      <p className="text-gray-600 mb-6">Contribute your personal narrative or historical memory to Ekiti30Digital.</p>

      {statusMessage && (
        <div
          className={`p-4 mb-4 rounded-md text-sm font-medium ${
            statusMessage.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'
          }`}
        >
          {statusMessage.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
          <input
            type="text"
            name="fullName"
            required
            value={formData.fullName}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="e.g. Adebayo Ogundele"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
          <input
            type="email"
            name="email"
            required
            value={formData.email}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Story Title</label>
          <input
            type="text"
            name="title"
            required
            value={formData.title}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Give your story a meaningful title"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Category / Sector</label>
          <select
            name="category"
            value={formData.category}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="Education">Education</option>
            <option value="Health">Health</option>
            <option value="Agriculture">Agriculture</option>
            <option value="Culture & Heritage">Culture & Heritage</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Your Story</label>
          <textarea
            name="content"
            rows={5}
            required
            value={formData.content}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Write your story here..."
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full py-2 px-4 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-md transition duration-200 disabled:opacity-50"
        >
          {isSubmitting ? 'Submitting...' : 'Submit Story'}
        </button>
      </form>
    </section>
  );
};
