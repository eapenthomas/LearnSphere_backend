import React from 'react';
import { motion } from 'framer-motion';

const Button = ({
    children,
    variant = 'primary',
    onClick,
    disabled = false,
    className = '',
    type = 'button',
    fullWidth = false
}) => {
    const baseClasses = 'font-medium py-3 px-6 rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 transform';

    const variants = {
        primary: 'bg-primary-600 hover:bg-primary-700 text-white shadow-elegant hover:shadow-elegant-lg focus:ring-primary-500 hover:-translate-y-0.5',
        secondary: 'bg-secondary-600 hover:bg-secondary-700 text-white shadow-elegant hover:shadow-elegant-lg focus:ring-secondary-600 hover:-translate-y-0.5',
        blue: 'bg-blue-500 hover:bg-blue-600 text-white shadow-elegant hover:shadow-elegant-lg focus:ring-blue-500 hover:-translate-y-0.5',
        outline: 'bg-transparent hover:bg-primary-50 text-primary-600 border-2 border-primary-600 hover:border-primary-700 focus:ring-primary-500 hover:-translate-y-0.5',
        'blue-outline': 'bg-transparent hover:bg-blue-50 text-blue-600 border-2 border-blue-500 hover:border-blue-600 focus:ring-blue-500 hover:-translate-y-0.5',
        danger: 'bg-error-500 hover:bg-error-600 text-white shadow-elegant hover:shadow-elegant-lg focus:ring-error-500 hover:-translate-y-0.5',
        ghost: 'bg-transparent hover:bg-background-tertiary text-text-primary focus:ring-secondary-600'
    };

    const widthClass = fullWidth ? 'w-full' : '';
    const disabledClass = disabled ? 'opacity-50 cursor-not-allowed transform-none' : 'cursor-pointer';

    return (
        <motion.button
            type={type}
            onClick={onClick}
            disabled={disabled}
            className={`${baseClasses} ${variants[variant]} ${widthClass} ${disabledClass} ${className}`}
            whileHover={!disabled ? { scale: 1.02 } : {}}
            whileTap={!disabled ? { scale: 0.98 } : {}}
        >
            {children}
        </motion.button>
    );
};

export default Button;