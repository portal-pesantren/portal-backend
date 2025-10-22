# Portal Pesantren - Frontend Development Plan

## 📋 Deskripsi Project

Portal Pesantren adalah platform digital yang menghubungkan orang tua dengan pesantren terbaik di Indonesia. Platform ini menyediakan sistem pencarian pesantren, proses pendaftaran, konsultasi, dan manajemen konten yang komprehensif.

## 🛠️ Tech Stack

- **Framework**: Next.js 15 dengan App Router
- **UI Library**: React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **State Management**: React Query (TanStack Query)
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Development**: ESLint, Turbopack

## 🎯 Fitur Utama Berdasarkan API Endpoints

### 1. **Authentication & User Management**
- **Endpoints**: `/api/v1/users/register`, `/api/v1/users/login`, `/api/v1/users/logout`
- **Fitur**:
  - Registrasi pengguna baru
  - Login/logout sistem
  - Manajemen profil pengguna
  - Update informasi pribadi
  - Sistem role-based (user/admin)

### 2. **Pesantren Management**
- **Endpoints**: `/api/v1/pesantren/*`
- **Fitur**:
  - Pencarian dan filter pesantren
  - Detail informasi pesantren
  - Pesantren unggulan dan populer
  - Statistik pesantren
  - CRUD pesantren (admin only)
  - Set featured pesantren (admin only)

### 3. **News & Content Management**
- **Endpoints**: `/api/v1/news/*`
- **Fitur**:
  - Daftar berita dengan pagination
  - Detail berita
  - Berita unggulan dan populer
  - Statistik berita
  - Filter berdasarkan kategori

### 4. **Review System**
- **Endpoints**: `/api/v1/reviews/*`
- **Fitur**:
  - Sistem rating dan ulasan pesantren
  - Membuat ulasan baru
  - Filter ulasan berdasarkan rating
  - Verifikasi ulasan

### 5. **Application System**
- **Endpoints**: `/api/v1/applications/*`
- **Fitur**:
  - Pendaftaran ke pesantren
  - Tracking status aplikasi
  - Manajemen aplikasi (admin)
  - Update status aplikasi

### 6. **Consultation System**
- **Endpoints**: `/api/v1/consultations/*`
- **Fitur**:
  - Sistem konsultasi online
  - Kategori konsultasi
  - Status tracking konsultasi
  - Priority management

### 7. **Dashboard & Analytics**
- **Endpoints**: `/health`, `/api/v1/*/stats`
- **Fitur**:
  - Health check system
  - Dashboard statistik
  - Analytics pesantren, berita, dll

## 🏗️ Struktur Project Frontend

```
portal-pesantren-frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth group routes
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/              # Dashboard group routes
│   │   ├── admin/
│   │   │   ├── pesantren/
│   │   │   ├── applications/
│   │   │   ├── consultations/
│   │   │   └── users/
│   │   └── user/
│   │       ├── profile/
│   │       ├── applications/
│   │       └── consultations/
│   ├── pesantren/
│   │   ├── page.tsx              # List pesantren
│   │   └── [id]/
│   │       └── page.tsx          # Detail pesantren
│   ├── news/
│   │   ├── page.tsx              # List berita
│   │   └── [id]/
│   │       └── page.tsx          # Detail berita
│   ├── reviews/
│   │   └── page.tsx              # List reviews
│   ├── about/
│   ├── contact/
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx                  # Homepage
├── components/                   # Reusable components
│   ├── ui/                       # Base UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── modal.tsx
│   │   ├── pagination.tsx
│   │   └── loading.tsx
│   ├── layout/                   # Layout components
│   │   ├── header.tsx
│   │   ├── footer.tsx
│   │   ├── sidebar.tsx
│   │   └── navigation.tsx
│   ├── forms/                    # Form components
│   │   ├── auth-form.tsx
│   │   ├── pesantren-form.tsx
│   │   ├── review-form.tsx
│   │   ├── application-form.tsx
│   │   └── consultation-form.tsx
│   ├── cards/                    # Card components
│   │   ├── pesantren-card.tsx
│   │   ├── news-card.tsx
│   │   ├── review-card.tsx
│   │   └── stats-card.tsx
│   ├── filters/                  # Filter components
│   │   ├── pesantren-filter.tsx
│   │   ├── news-filter.tsx
│   │   └── review-filter.tsx
│   └── dashboard/                # Dashboard components
│       ├── admin-dashboard.tsx
│       ├── user-dashboard.tsx
│       └── analytics-chart.tsx
├── lib/                          # Utility libraries
│   ├── api/                      # API client setup
│   │   ├── client.ts             # Axios configuration
│   │   ├── auth.ts               # Auth API calls
│   │   ├── pesantren.ts          # Pesantren API calls
│   │   ├── news.ts               # News API calls
│   │   ├── reviews.ts            # Reviews API calls
│   │   ├── applications.ts       # Applications API calls
│   │   └── consultations.ts      # Consultations API calls
│   ├── hooks/                    # Custom React hooks
│   │   ├── use-auth.ts
│   │   ├── use-pesantren.ts
│   │   ├── use-news.ts
│   │   ├── use-reviews.ts
│   │   ├── use-applications.ts
│   │   └── use-consultations.ts
│   ├── utils/                    # Utility functions
│   │   ├── format.ts
│   │   ├── validation.ts
│   │   └── constants.ts
│   ├── types/                    # TypeScript type definitions
│   │   ├── auth.ts
│   │   ├── pesantren.ts
│   │   ├── news.ts
│   │   ├── reviews.ts
│   │   ├── applications.ts
│   │   ├── consultations.ts
│   │   └── api.ts
│   └── providers/                # Context providers
│       ├── auth-provider.tsx
│       ├── query-provider.tsx
│       └── theme-provider.tsx
├── public/                       # Static assets
│   ├── images/
│   ├── icons/
│   └── favicon.ico
├── styles/                       # Additional styles
│   └── globals.css
├── .env.local                    # Environment variables
├── .env.example
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── package.json
└── README.md
```

## 🔧 Setup & Configuration

### 1. **Environment Variables**
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Portal Pesantren
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### 2. **API Client Configuration**
```typescript
// lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor untuk menambahkan token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### 3. **React Query Setup**
```typescript
// lib/providers/query-provider.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export default function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        cacheTime: 10 * 60 * 1000, // 10 minutes
      },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

## 📱 Halaman & Fitur Detail

### 1. **Homepage (`/`)**
- Hero section dengan statistik pesantren
- Featured pesantren carousel
- Popular pesantren grid
- Latest news section
- Call-to-action untuk registrasi

### 2. **Authentication Pages**
- **Login (`/login`)**
  - Form login dengan email/password
  - Remember me option
  - Forgot password link
  - Social login (optional)

- **Register (`/register`)**
  - Form registrasi dengan validasi
  - Terms & conditions checkbox
  - Email verification flow

### 3. **Pesantren Pages**
- **List Pesantren (`/pesantren`)**
  - Search bar dengan autocomplete
  - Advanced filters (lokasi, program, biaya, dll)
  - Grid/list view toggle
  - Pagination
  - Sort options (rating, popularity, newest)

- **Detail Pesantren (`/pesantren/[id]`)**
  - Comprehensive pesantren information
  - Image gallery dengan lightbox
  - Video preview
  - Reviews & ratings section
  - Application form
  - Contact information
  - Location map integration

### 4. **News Pages**
- **List News (`/news`)**
  - Featured news carousel
  - Category filter
  - Search functionality
  - Pagination
  - Popular/latest tabs

- **Detail News (`/news/[id]`)**
  - Full article content
  - Related articles
  - Social sharing buttons
  - Comments section (optional)

### 5. **User Dashboard (`/dashboard/user`)**
- **Profile Management**
  - Edit personal information
  - Change password
  - Avatar upload

- **My Applications**
  - List of submitted applications
  - Status tracking
  - Application details

- **My Consultations**
  - Active consultations
  - Consultation history
  - Create new consultation

### 6. **Admin Dashboard (`/dashboard/admin`)**
- **Analytics Overview**
  - Key metrics cards
  - Charts & graphs
  - Recent activities

- **Pesantren Management**
  - CRUD operations
  - Bulk actions
  - Featured status management

- **Application Management**
  - Review applications
  - Status updates
  - Bulk processing

- **User Management**
  - User list with filters
  - User details
  - Account activation/deactivation

## 🎨 UI/UX Design Guidelines

### 1. **Design System**
- **Colors**: Islamic-inspired color palette (green, gold, white)
- **Typography**: Clean, readable fonts (Inter, Poppins)
- **Spacing**: Consistent 8px grid system
- **Border Radius**: Rounded corners for modern look

### 2. **Component Standards**
- Responsive design (mobile-first)
- Accessibility compliance (WCAG 2.1)
- Loading states untuk semua async operations
- Error handling dengan user-friendly messages
- Form validation dengan real-time feedback

### 3. **Performance Optimization**
- Image optimization dengan Next.js Image component
- Lazy loading untuk components
- Code splitting per route
- Caching strategy dengan React Query

## 🔄 State Management Strategy

### 1. **Server State (React Query)**
- API data caching
- Background refetching
- Optimistic updates
- Error handling

### 2. **Client State (React Context/useState)**
- Authentication state
- UI state (modals, filters)
- Form state
- Theme preferences

### 3. **Local Storage**
- Authentication tokens
- User preferences
- Form drafts

## 🧪 Testing Strategy

### 1. **Unit Testing**
- Component testing dengan React Testing Library
- Utility function testing
- Custom hooks testing

### 2. **Integration Testing**
- API integration testing
- Form submission flows
- Authentication flows

### 3. **E2E Testing (Optional)**
- Critical user journeys
- Cross-browser compatibility

## 🚀 Development Phases

### **Phase 1: Foundation (Week 1-2)**
- Project setup & configuration
- Basic layout components
- Authentication system
- API client setup

### **Phase 2: Core Features (Week 3-4)**
- Pesantren listing & detail pages
- Search & filter functionality
- User dashboard
- Review system

### **Phase 3: Advanced Features (Week 5-6)**
- Application system
- Consultation system
- News management
- Admin dashboard

### **Phase 4: Polish & Optimization (Week 7-8)**
- UI/UX improvements
- Performance optimization
- Testing & bug fixes
- Documentation

## 📚 API Integration Mapping

### **Authentication Endpoints**
- `POST /api/v1/users/register` → Register form
- `POST /api/v1/users/login` → Login form
- `POST /api/v1/users/logout` → Logout functionality
- `GET /api/v1/users/profile` → User profile page
- `PUT /api/v1/users/profile` → Profile update form

### **Pesantren Endpoints**
- `GET /api/v1/pesantren` → Pesantren listing page
- `GET /api/v1/pesantren/{id}` → Pesantren detail page
- `GET /api/v1/pesantren/featured` → Homepage featured section
- `GET /api/v1/pesantren/popular` → Homepage popular section
- `GET /api/v1/pesantren/stats` → Dashboard statistics

### **News Endpoints**
- `GET /api/v1/news` → News listing page
- `GET /api/v1/news/{id}` → News detail page
- `GET /api/v1/news/featured` → Homepage news section
- `GET /api/v1/news/popular` → Popular news section

### **Review Endpoints**
- `GET /api/v1/reviews` → Reviews listing
- `POST /api/v1/reviews` → Create review form
- Reviews integration dalam pesantren detail page

### **Application Endpoints**
- `GET /api/v1/applications` → User applications dashboard
- `POST /api/v1/applications` → Application form
- Admin application management

### **Consultation Endpoints**
- `GET /api/v1/consultations` → User consultations dashboard
- `POST /api/v1/consultations` → Consultation form
- Admin consultation management

## 🔒 Security Considerations

### 1. **Authentication & Authorization**
- JWT token management
- Role-based access control
- Protected routes
- Token refresh mechanism

### 2. **Data Validation**
- Client-side validation
- Server-side validation
- Input sanitization
- XSS protection

### 3. **API Security**
- HTTPS enforcement
- Rate limiting awareness
- Error handling tanpa expose sensitive data

## 📈 Performance Metrics

### 1. **Core Web Vitals**
- Largest Contentful Paint (LCP) < 2.5s
- First Input Delay (FID) < 100ms
- Cumulative Layout Shift (CLS) < 0.1

### 2. **Loading Performance**
- Time to Interactive < 3s
- Bundle size optimization
- Image optimization

### 3. **User Experience**
- Mobile responsiveness
- Accessibility score > 90
- SEO optimization

## 🎯 Success Criteria

### 1. **Functional Requirements**
- ✅ Semua API endpoints terintegrasi
- ✅ Authentication & authorization working
- ✅ CRUD operations untuk semua entities
- ✅ Search & filter functionality
- ✅ Responsive design

### 2. **Non-Functional Requirements**
- ✅ Performance benchmarks tercapai
- ✅ Accessibility compliance
- ✅ Cross-browser compatibility
- ✅ SEO optimization
- ✅ Error handling & user feedback

### 3. **Business Requirements**
- ✅ User dapat mencari & mendaftar ke pesantren
- ✅ Admin dapat mengelola data pesantren
- ✅ Sistem konsultasi berfungsi
- ✅ Review & rating system aktif
- ✅ News & content management working

---

**Dokumen ini akan menjadi panduan utama dalam pengembangan frontend Portal Pesantren. Setiap fase development harus mengacu pada rancangan ini untuk memastikan konsistensi dan kualitas hasil akhir.**