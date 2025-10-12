import React, { useState } from 'react';
import { motion } from 'framer-motion';

const Input = ({
    label,
    type = 'text',
    value,
    onChange,
    error,
    placeholder,
    required = false,
    className = '',
    ...props
}) => {
    const [isFocused, setIsFocused] = useState(false);
    const [hasValue, setHasValue] = useState(!!value);

    const handleChange = (e) => {
        setHasValue(!!e.target.value);
        onChange(e);
    };

    const handleFocus = () => setIsFocused(true);
    const handleBlur = () => setIsFocused(false);

    return (
        <div className={`relative ${className}`}>
            <div className="relative">
                <input
                    type={type}
                    value={value}
                    onChange={handleChange}
                    onFocus={handleFocus}
                    onBlur={handleBlur}
                    placeholder={placeholder}
                    required={required}
                    className={`
            form-input font-sans
            ${error ? 'border-error-500 focus:border-error-500 focus:ring-error-500/20' : ''}
            ${hasValue || isFocused ? 'pt-6 pb-2' : 'py-3'}
          `}
                    {...props}
                />
                {(hasValue || isFocused) && (
                    <motion.label
                        initial={{ opacity: 0, y: 0 }}
                        animate={{ opacity: 1, y: -8 }}
                        className={`
              absolute left-4 top-2 text-body-sm font-medium transition-colors duration-300 font-sans
              ${error ? 'text-error-500' : 'text-secondary-600'}
            `}
                    >
                        {label}
                        {required && <span className="text-error-500 ml-1">*</span>}
                    </motion.label>
                )}
            </div>
            {error && (
                <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-error-500 text-body-md mt-1 ml-1 font-sans"
                >
                    {error}
                </motion.p>
            )}
        </div>
    );
};

export default Input; 