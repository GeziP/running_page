import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserProfile } from '../components/UserProfileManager';

interface UserProfileContextType {
  userProfile: UserProfile | null;
  setUserProfile: (profile: UserProfile | null) => void;
  updateProfile: (updates: Partial<UserProfile>) => void;
  hasProfile: boolean;
}

const UserProfileContext = createContext<UserProfileContextType | undefined>(undefined);

export const useUserProfile = () => {
  const context = useContext(UserProfileContext);
  if (context === undefined) {
    throw new Error('useUserProfile must be used within a UserProfileProvider');
  }
  return context;
};

interface UserProfileProviderProps {
  children: ReactNode;
}

export const UserProfileProvider: React.FC<UserProfileProviderProps> = ({ children }) => {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    // 从localStorage加载用户配置
    const loadProfile = () => {
      try {
        const savedProfile = localStorage.getItem('userProfile');
        if (savedProfile) {
          const profile = JSON.parse(savedProfile);
          setUserProfile(profile);
        }
      } catch (error) {
        console.error('Failed to load user profile from localStorage:', error);
      }
    };

    loadProfile();
  }, []);

  const updateProfile = (updates: Partial<UserProfile>) => {
    if (userProfile) {
      const updatedProfile = { ...userProfile, ...updates };
      setUserProfile(updatedProfile);
      // 保存到localStorage
      try {
        localStorage.setItem('userProfile', JSON.stringify(updatedProfile));
      } catch (error) {
        console.error('Failed to save user profile to localStorage:', error);
      }
    }
  };

  const setUserProfileAndSave = (profile: UserProfile | null) => {
    setUserProfile(profile);
    if (profile) {
      try {
        localStorage.setItem('userProfile', JSON.stringify(profile));
      } catch (error) {
        console.error('Failed to save user profile to localStorage:', error);
      }
    } else {
      try {
        localStorage.removeItem('userProfile');
      } catch (error) {
        console.error('Failed to remove user profile from localStorage:', error);
      }
    }
  };

  const value: UserProfileContextType = {
    userProfile,
    setUserProfile: setUserProfileAndSave,
    updateProfile,
    hasProfile: !!userProfile
  };

  return (
    <UserProfileContext.Provider value={value}>
      {children}
    </UserProfileContext.Provider>
  );
}; 