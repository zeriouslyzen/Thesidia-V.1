#!/usr/bin/env python3
"""
Generate Bot Army
Creates realistic bot profiles with synthesized activity
Minimal resource usage - uses caching and templates
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'webapp'))

from webapp.social.bot_generator import BotGenerator


def main():
    """Generate bots with activity"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate bot profiles and activity')
    parser.add_argument('--count', type=int, default=10, help='Number of bots to generate')
    parser.add_argument('--types', nargs='+', default=['active', 'moderate', 'casual'],
                       help='Bot types to generate')
    parser.add_argument('--no-activity', action='store_true', help='Skip activity generation')
    parser.add_argument('--days', type=int, default=30, help='Days of activity to generate')
    parser.add_argument('--network', action='store_true', help='Build network between bots')
    parser.add_argument('--use-thesidia', action='store_true', help='Use Thesidia for sophisticated content (slower but higher quality)')
    parser.add_argument('--community', action='store_true', help='Generate community bots instead of regular bots')
    parser.add_argument('--communities', nargs='+', help='Specific communities to create bots for')
    parser.add_argument('--bots-per-community', type=int, default=3, help='Number of bots per community')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Intelligent Bot Generator")
    print("=" * 60)
    if args.community:
        print(f"\n🏘️  Generating Community Bots...")
        print(f"   Communities: {', '.join(args.communities) if args.communities else 'Auto-generated'}")
        print(f"   Bots per community: {args.bots_per_community}")
    else:
        print(f"\n🤖 Generating {args.count} bots...")
        print(f"   Types: {', '.join(args.types)}")
    print(f"   Activity: {'No' if args.no_activity else f'Yes ({args.days} days)'}")
    print(f"   Network: {'Yes' if args.network else 'No'}")
    print(f"   Content: {'Thesidia (sophisticated)' if args.use_thesidia else 'Templates (fast)'}")
    print()
    
    # Optionally load Thesidia for sophisticated content
    thesidia_instance = None
    if args.use_thesidia:
        try:
            from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
            print("Loading Thesidia for sophisticated content generation...")
            thesidia_instance = ThesidiaHybridAdaptive(model="clean-mistral:latest")
            thesidia_instance.load_state()
            print("✅ Thesidia loaded")
        except Exception as e:
            print(f"⚠️  Could not load Thesidia: {e}")
            print("   Falling back to template-based generation")
            args.use_thesidia = False
    
    bot_generator = BotGenerator(
        base_dir=project_root,
        use_thesidia=args.use_thesidia,
        thesidia_instance=thesidia_instance
    )
    
    try:
        if args.community:
            # Generate community bots
            result = bot_generator.generate_community_bots(
                communities=args.communities,
                bots_per_community=args.bots_per_community,
                generate_activity=not args.no_activity,
                days_of_activity=args.days
            )
            print(f"   Communities: {', '.join(result.get('communities', []))}")
        else:
            # Generate regular bots
            result = bot_generator.generate_bot_army(
                count=args.count,
                bot_types=args.types,
                generate_activity=not args.no_activity,
                days_of_activity=args.days
            )
        
        print("=" * 60)
        print("✅ Bot Generation Complete!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   - {result['bots_created']} bots created")
        print(f"   - {result['network_connections']} network connections")
        
        if args.community and 'communities' in result:
            print(f"   - Communities: {', '.join(result['communities'])}")
        
        if not args.no_activity:
            print(f"\n📝 Bot Activity:")
            for bot in result['bots'][:10]:  # Show first 10
                community_info = f" [{bot.get('community', '')}]" if bot.get('community') else ""
                print(f"   - @{bot['username']} ({bot['bot_type']}{community_info})")
            if len(result['bots']) > 10:
                print(f"   ... and {len(result['bots']) - 10} more")
        
        print("\n🎉 Bots are now active in the system!")
        print("   View them in the stream feed at /stream.html")
        if args.community:
            print("   Community bots appear in the Communities feed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

