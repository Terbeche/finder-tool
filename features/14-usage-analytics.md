# Usage Analytics

## Overview
Comprehensive file usage tracking and analytics system that monitors file access patterns, provides storage insights, and generates actionable recommendations for file management and cleanup.

## Need/Purpose
- Track which files are actually being used vs. taking up space
- Identify cleanup candidates (large, rarely accessed files)
- Provide storage cost analysis and optimization suggestions
- Help users make informed decisions about file organization
- Monitor file access patterns to improve workflow efficiency

## Features Implemented
- ✅ Real-time file access tracking with timestamps
- ✅ Usage frequency analysis (most/least accessed files)
- ✅ Storage breakdown by file type with size and count statistics
- ✅ Cleanup candidates identification (large, rarely accessed files)
- ✅ Storage cost calculator with configurable rates
- ✅ Intelligent recommendations based on usage patterns
- ✅ Analytics report export functionality
- ✅ Visual analytics dashboard with multiple tabs

## How to Test

### Basic Usage Tracking
1. Search for files and select them in the results table
2. Open files using the "Open File" button or preview panel
3. Go to Tools → Usage Analytics to see tracked access data
4. **Expected Result**: Files you opened show in "Most Frequently Accessed" table

### Storage Analysis
1. Search a directory with various file types
2. Open Usage Analytics → Storage Analysis tab
3. **Expected Result**: See breakdown by file type with sizes and percentages
4. **Expected Result**: Largest files listed in order of size

### Cleanup Recommendations
1. Search a directory with large files (>50MB)
2. Don't access some of the large files
3. Open Usage Analytics → File Access tab
4. **Expected Result**: Rarely accessed large files appear in cleanup candidates

### Analytics Export
1. Generate some usage data by accessing files
2. In Usage Analytics dialog, click "Export Analytics Report"
3. Save the report file
4. **Expected Result**: Text file with comprehensive analytics data

### Real-time Updates
1. Keep Usage Analytics dialog open
2. Access files from main window
3. **Expected Result**: Analytics update automatically every 10 seconds

## Technical Implementation

### UsageAnalytics Class
- **Data Structure**: Dictionary mapping file paths to access data
- **Persistence**: In-memory storage (resets on app restart)
- **Access Recording**: Automatic tracking when files are opened or previewed
- **Cost Calculation**: Configurable cost per GB for storage estimation

### Analytics Dialog Components
- **Overview Tab**: Storage statistics and recommendations summary
- **File Access Tab**: Most/least accessed files with cleanup candidates
- **Storage Analysis Tab**: File type breakdown and largest files analysis
- **Real-time Updates**: Auto-refresh every 10 seconds while dialog is open

### Integration Points
- **Main Window**: Records access when files are opened
- **Preview Panel**: Records access when files are previewed
- **Menu Integration**: Available via Tools → Usage Analytics
- **Export System**: Generates comprehensive text reports

## Usage Scenarios

### Storage Cleanup
1. **Large File Identification**: Find biggest files consuming space
2. **Access Pattern Analysis**: Identify files never or rarely accessed
3. **Cleanup Candidates**: Get prioritized list of files safe to remove
4. **Storage Savings**: Calculate potential space recovery

### Workflow Optimization
1. **Frequently Used Files**: Identify most important files for quick access
2. **File Type Analysis**: Understand storage distribution by type
3. **Cost Analysis**: Monitor storage costs for budget planning
4. **Usage Patterns**: Track how file access changes over time

## Configuration Options

### Storage Cost Settings
- **Cost per GB**: Configurable rate for storage cost calculation (default: $0.10/GB/month)
- **Update Frequency**: Real-time refresh interval (default: 10 seconds)
- **Cleanup Threshold**: Minimum file size for cleanup candidates (default: 50MB)
- **Access Timeout**: Days without access to consider file "rarely used" (default: 30 days)

### Display Options
- **Table Limits**: Number of files shown in each table (configurable)
- **Time Format**: Display format for timestamps and dates
- **Size Format**: Human-readable size formatting
- **Export Format**: Text-based analytics reports

## Analytics Metrics

### Storage Metrics
- **Total Files**: Count of all scanned files
- **Total Size**: Combined size of all files
- **Average File Size**: Mean file size across all files
- **Largest File**: Single biggest file identified

### Usage Metrics
- **Files Accessed**: Count of files with recorded access
- **Never Accessed**: Files with zero access count
- **Recently Accessed**: Files accessed within last 7 days
- **Access Frequency**: Average access count per file

### Cost Metrics
- **Monthly Storage Cost**: Estimated cost based on file sizes
- **Cost per Access**: Storage cost divided by access frequency
- **Cleanup Savings**: Potential cost reduction from removing unused files

## Recommendations Engine

### Cleanup Suggestions
- **Large Unused Files**: Files >50MB with no recent access
- **Old Files**: Files not accessed in 30+ days
- **Duplicate-prone Types**: File types with high counts
- **Storage Hotspots**: File types consuming most space

### Optimization Tips
- **Archive Candidates**: Old, large files suitable for archiving
- **Cloud Migration**: Rarely accessed files good for cloud storage
- **Workflow Improvements**: Suggestions based on access patterns
- **Cost Optimization**: Ways to reduce storage expenses

## Known Limitations

### Current Limitations
- **Session-based Tracking**: Usage data resets when application restarts
- **No Historical Trends**: No long-term usage pattern analysis
- **Manual Cost Rates**: Storage costs not automatically updated
- **Local Files Only**: No tracking for network or cloud files

### Performance Considerations
- **Memory Usage**: Usage data grows with tracked files
- **Real-time Updates**: Small performance impact during updates
- **Large Datasets**: May slow down with thousands of tracked files

## Future Enhancements

### Planned Improvements
- **Persistent Storage**: Save usage data between sessions
- **Historical Analysis**: Track usage trends over time
- **Automated Cleanup**: Schedule automatic cleanup of unused files
- **Cloud Integration**: Track usage across cloud storage services
- **Advanced Analytics**: Machine learning for usage prediction

### Advanced Features
- **Usage Heatmaps**: Visual representation of file access patterns
- **Predictive Analytics**: Forecast storage needs and costs
- **Team Analytics**: Multi-user usage tracking and analysis
- **Integration APIs**: Connect with other storage management tools

## Troubleshooting

### Common Issues

**Problem**: Usage data not updating
**Solutions**:
- Ensure files are being opened through the application
- Check that analytics dialog is refreshing (10-second timer)
- Verify file paths are accessible and valid

**Problem**: Cost calculations seem incorrect
**Solutions**:
- Check cost per GB setting (default $0.10)
- Verify file sizes are being calculated correctly
- Consider whether estimate includes all storage factors

**Problem**: No cleanup candidates shown
**Solutions**:
- Ensure you have files larger than 50MB in scan results
- Access some files to create usage patterns
- Check that enough time has passed to establish "rarely accessed" status

## Related Features

- **File Scanning**: Provides file data for analysis
- **Preview Panel**: Records access when files are previewed
- **Security Features**: Complementary file analysis tools
- **Export System**: Shares report generation framework
- **Performance Optimization**: Memory usage considerations

## Security Considerations

- **Privacy**: File access tracking is local only, no external reporting
- **Data Protection**: Usage data stored in memory, not persisted to disk
- **Path Security**: File paths validated before tracking access
- **Resource Limits**: Memory usage bounded to prevent system impact

## Testing Checklist

- [ ] File access tracking works when opening files
- [ ] Preview panel access triggers usage recording
- [ ] Analytics tables populate with correct data
- [ ] Real-time updates refresh dialog content
- [ ] Storage breakdown calculates correctly
- [ ] Cleanup candidates identify appropriate files
- [ ] Export functionality generates complete reports
- [ ] Cost calculations use correct rates
- [ ] Recommendations provide actionable insights
- [ ] Dialog performance remains responsive with large datasets
